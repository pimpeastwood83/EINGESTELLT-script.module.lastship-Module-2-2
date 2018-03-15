

import time
import datetime
import cache
from resources.lib.modules import control


try:
    from sqlite3 import dbapi2 as db, OperationalError
except ImportError:
    from pysqlite2 import dbapi2 as db, OperationalError

faultTable = "faultLog"

######### Tags
tagSearch = "SEARCH"
tagResolve = "RESOLVE"
tagScrape = "SCRAPE"
tagDisabled = "DISABLED"

######### Settings
maxFaultsPerDay = int(control.setting('FaultLogger.numErrors'))
triggerCacheSetting = "source_fault_last_seen"

def init():
    now = int(time.time())
    timelimit = now - 60*60*int(control.setting('FaultLogger.recheckHours'))
    lastSeen = cache.cache_get(triggerCacheSetting)
    if lastSeen is not None and int(lastSeen["value"]) > timelimit:
        return

    try:
        dbcon = db.connect(control.providercacheFile)
        dbcur = dbcon.cursor()
        dbcur.executescript("CREATE TABLE IF NOT EXISTS %s (ID Integer PRIMARY KEY AUTOINCREMENT, provider TEXT, tag TEXT, date INTEGER);" % faultTable)
        dbcur.execute("DELETE FROM %s WHERE date < ?;" % faultTable, (timelimit,))
        dbcon.commit()
        dbcur.close()
        del dbcur
        dbcon.close()
    except:
        pass

    cache.cache_insert(triggerCacheSetting, now)

def logFault(provider, tag):
    now = int(time.time())
    try:
        dbcon = db.connect(control.providercacheFile)
        dbcur = dbcon.cursor()
        dbcur.execute("INSERT INTO %s VALUES (null,?,?,?)" % faultTable, (provider, tag, now))
        dbcon.commit()
        dbcur.execute("SELECT COUNT(*) FROM %s WHERE provider=? AND tag <> ? " %faultTable, (provider, tagDisabled))
        num_latest_faults = dbcur.fetchone()[0]
        if num_latest_faults >= maxFaultsPerDay:
            dbcur.execute("INSERT INTO %s VALUES (null,?,?,?)" % faultTable, (provider, tagDisabled, now))
            dbcon.commit()
        dbcur.close()
        del dbcur
        dbcon.close()
    except:
        pass
    return

def isEnabled(provider):
    try:
        dbcon = db.connect(control.providercacheFile)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT COUNT(*) FROM %s WHERE provider=? AND tag = ?" % faultTable,
                      (provider, tagDisabled))
        numDisabled = dbcur.fetchone()[0]
        dbcur.close()
        del dbcur
        dbcon.close()
        if numDisabled > 0:
            return False
    except:
        return True
    return True

def getFaultInfoString():
    faults = getFaults()
    if faults is None or len(faults) == 0 : return "Keine";

    info = ""

    for faultProvider in faults:
        fptime = datetime.datetime.fromtimestamp(faultProvider[2]).strftime('%d.%m.%Y %H:%M:%S')
        if faultProvider[3] == tagDisabled:
            info += "[COLOR red]"
        info += faultProvider[0] + ", "+str(faultProvider[1])+" mal, zuletzt: "+fptime
        if faultProvider[3] == tagDisabled:
            info += "[/COLOR]\n"
        else:
            info += ", tag: "+faultProvider[3]+"\n"

    return info



def getFaults():
    try:
        dbcon = db.connect(control.providercacheFile)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT provider, COUNT(provider), date, tag as faults FROM %s Group By provider Order By count(provider) DESC, date ASC" %faultTable)
        res = dbcur.fetchall()
        dbcur.close()
        del dbcur
        dbcon.close()
        return res
    except:
        return None