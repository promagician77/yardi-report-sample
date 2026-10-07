# Aged delinquency — a worked Yardi sample

Static site, no build step. Five tabs: the security demonstration, the rendered report,
the stored procedure, upgrade-safety notes, and working notes.

Every figure on the first tab is a real query result. Rebuild them with:

    python build_db.py     # synthetic Voyager-shaped SQLite database
    python run_report.py   # runs the report three ways, writes site/report_data.json

`files/rpt_aged_delinquency.sql` is the deliverable itself — T-SQL for Voyager, with the
user's property list as a CTE that every other join passes through.

Run locally: `npm start` → http://localhost:3000
Deploy: `npm run deploy`, or import the folder in Vercel ("Other" preset, no build command).
