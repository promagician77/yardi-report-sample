"""Aged delinquency, run three ways, to show what the security filter is worth."""
import sqlite3, json
db = sqlite3.connect("voyager_demo.db"); db.row_factory = sqlite3.Row
AS_OF = "2026-09-30"

BUCKETS = """
    SUM(CASE WHEN julianday(:asof)-julianday(a.dtPost) <= 30 THEN a.cOpenAmount ELSE 0 END) AS b0,
    SUM(CASE WHEN julianday(:asof)-julianday(a.dtPost) BETWEEN 31 AND 60 THEN a.cOpenAmount ELSE 0 END) AS b31,
    SUM(CASE WHEN julianday(:asof)-julianday(a.dtPost) BETWEEN 61 AND 90 THEN a.cOpenAmount ELSE 0 END) AS b61,
    SUM(CASE WHEN julianday(:asof)-julianday(a.dtPost) > 90 THEN a.cOpenAmount ELSE 0 END) AS b91,
    SUM(a.cOpenAmount) AS total"""

def query(secure, user=None):
    """secure=False is the report most people write. secure=True is the one that ships."""
    sec = ("""JOIN userproperty up ON up.hProperty = p.hMy
              JOIN cuser u ON u.hMy = up.hUser AND u.sUserName = :user""" if secure else "")
    sql = f"""
    SELECT p.sCode, p.sName, t.sName AS tenant, un.sUnitCode, {BUCKETS}
    FROM artran a
      JOIN property p ON p.hMy = a.hProperty
      JOIN tenant   t ON t.hMy = a.hTenant
      JOIN unit    un ON un.hMy = t.hUnit
      {sec}
    WHERE a.cOpenAmount > 0 AND a.iType = 1 AND a.dtPost <= :asof
    GROUP BY p.sCode, p.sName, t.sName, un.sUnitCode
    HAVING SUM(a.cOpenAmount) > 0
    ORDER BY p.sName, t.sName"""
    return [dict(r) for r in db.execute(sql, {"asof": AS_OF, "user": user}).fetchall()]

def summarise(rows):
    return {"rows": len(rows), "properties": len({r["sCode"] for r in rows}),
            "tenants": len({(r["sCode"], r["tenant"]) for r in rows}),
            "total": round(sum(r["total"] for r in rows), 2),
            "over90": round(sum(r["b91"] for r in rows), 2)}

naive = query(False)
jsmith = query(True, "jsmith")
mchen = query(True, "mchen")
entitled = {r["sCode"] for r in jsmith}
leaked = {r["sCode"] for r in naive} - entitled
leaked_rows = [r for r in naive if r["sCode"] in leaked]

out = {
    "as_of": AS_OF,
    "naive": summarise(naive),
    "jsmith": {**summarise(jsmith), "name": "Jordan Smith", "role": "Regional Manager"},
    "mchen": {**summarise(mchen), "name": "Mei Chen", "role": "Portfolio Controller"},
    "leak": {"properties": sorted(leaked), "rows": len(leaked_rows),
             "amount": round(sum(r["total"] for r in leaked_rows), 2)},
    "entitled": sorted(entitled),
    "report_rows": jsmith,
}
json.dump(out, open("site/report_data.json", "w"), indent=2)
for k in ("naive", "jsmith", "mchen"):
    print(f"{k:8} rows={out[k]['rows']:4}  properties={out[k]['properties']}  AR=${out[k]['total']:,.2f}")
print(f"\nLEAK if the filter is omitted: {out['leak']['rows']} rows, "
      f"{len(out['leak']['properties'])} properties, ${out['leak']['amount']:,.2f}")
print("exposed:", ", ".join(out["leak"]["properties"]))
