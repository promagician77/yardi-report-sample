"""Synthetic Voyager-shaped database.

Mirrors Yardi's conventions closely enough for the point to land: hMy primary
keys, h-prefixed foreign keys, artran for AR activity, and a per-user property
list standing in for Voyager's security lists.
"""
import sqlite3, random, datetime as dt
random.seed(17)
db = sqlite3.connect("voyager_demo.db"); db.executescript("""
DROP TABLE IF EXISTS property; DROP TABLE IF EXISTS unit; DROP TABLE IF EXISTS tenant;
DROP TABLE IF EXISTS artran;   DROP TABLE IF EXISTS cuser; DROP TABLE IF EXISTS userproperty;
CREATE TABLE property(hMy INTEGER PRIMARY KEY, sCode TEXT, sName TEXT, sState TEXT, sRegion TEXT);
CREATE TABLE unit(hMy INTEGER PRIMARY KEY, hProperty INT, sUnitCode TEXT, sUnitType TEXT, cMarketRent REAL);
CREATE TABLE tenant(hMy INTEGER PRIMARY KEY, hProperty INT, hUnit INT, sName TEXT, dtMoveIn TEXT, sStatus TEXT);
CREATE TABLE artran(hMy INTEGER PRIMARY KEY, hProperty INT, hTenant INT, dtPost TEXT,
                    sChargeCode TEXT, cAmount REAL, cOpenAmount REAL, iType INT);
CREATE TABLE cuser(hMy INTEGER PRIMARY KEY, sUserName TEXT, sFullName TEXT, sRole TEXT);
CREATE TABLE userproperty(hUser INT, hProperty INT);
""")

PROPS = [("ashwd","Ashwood Commons","TX","South"), ("brkln","Brookline Park","MA","Northeast"),
         ("cdrcr","Cedar Creek Apartments","TX","South"), ("dvnpt","Davenport Lofts","IL","Midwest"),
         ("elmst","Elm Street Residences","MA","Northeast"), ("frsth","Forest Hill Manor","GA","Southeast"),
         ("grnvw","Grandview Terrace","CO","Mountain"), ("hrbrp","Harbor Point Flats","WA","Northwest")]
AS_OF = dt.date(2026, 9, 30)
TYPES = [("1BR1BA", 1450), ("2BR1BA", 1795), ("2BR2BA", 1995), ("3BR2BA", 2450), ("STUDIO", 1150)]
FIRST = "Alicia Marcus Priya Devon Rosa Ethan Naomi Caleb Imani Trevor Sofia Owen Lena Jamal Grace Hugo".split()
LAST = "Whitfield Okafor Lindqvist Barros Nakamura Delgado Fairweather Osei Kovacs Mbeki Castellanos Reyes".split()
CODES = ["RENT", "RENT", "RENT", "LATE", "UTIL", "PARK", "PETRENT"]

uid = tid = aid = 1
for p, (code, name, st, region) in enumerate(PROPS, start=1):
    db.execute("INSERT INTO property VALUES (?,?,?,?,?)", (p, code, name, st, region))
    for _ in range(random.randint(38, 72)):
        ut, mr = random.choice(TYPES)
        db.execute("INSERT INTO unit VALUES (?,?,?,?,?)",
                   (uid, p, f"{random.randint(1,4)}{random.randint(1,24):02d}", ut,
                    mr + random.randint(-90, 140)))
        if random.random() < 0.93:                      # most units occupied
            nm = f"{random.choice(FIRST)} {random.choice(LAST)}"
            db.execute("INSERT INTO tenant VALUES (?,?,?,?,?,?)",
                       (tid, p, uid, nm,
                        (AS_OF - dt.timedelta(days=random.randint(40, 1400))).isoformat(), "Current"))
            # roughly one tenant in six carries a balance
            if random.random() < 0.17:
                for _ in range(random.randint(1, 3)):
                    age = random.choice([random.randint(1, 30), random.randint(31, 60),
                                         random.randint(61, 90), random.randint(91, 240)])
                    amt = round(random.choice([mr, 75, 140, 55, 240]) * random.uniform(0.3, 1.0), 2)
                    db.execute("INSERT INTO artran VALUES (?,?,?,?,?,?,?,?)",
                               (aid, p, tid, (AS_OF - dt.timedelta(days=age)).isoformat(),
                                random.choice(CODES), amt, amt, 1)); aid += 1
            tid += 1
        uid += 1

# two real Voyager user shapes: a regional with a short list, a controller with all of it
db.execute("INSERT INTO cuser VALUES (1,'jsmith','Jordan Smith','Regional Manager')")
db.execute("INSERT INTO cuser VALUES (2,'mchen','Mei Chen','Portfolio Controller')")
for hp in (1, 3, 6):
    db.execute("INSERT INTO userproperty VALUES (1,?)", (hp,))
for hp in range(1, len(PROPS) + 1):
    db.execute("INSERT INTO userproperty VALUES (2,?)", (hp,))
db.commit()
print("properties", db.execute("SELECT COUNT(*) FROM property").fetchone()[0],
      "| units", db.execute("SELECT COUNT(*) FROM unit").fetchone()[0],
      "| tenants", db.execute("SELECT COUNT(*) FROM tenant").fetchone()[0],
      "| open AR rows", db.execute("SELECT COUNT(*) FROM artran").fetchone()[0])
