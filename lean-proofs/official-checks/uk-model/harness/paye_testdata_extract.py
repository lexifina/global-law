"""Extract HMRC 2025-26 PAYE tax test data (rest of UK, Scottish, Welsh) to JSONL, one line per sheet."""
import sys, json, openpyxl, glob
out = open(sys.argv[2], 'w')
for f in sorted(glob.glob(sys.argv[1] + '/*.xlsx')):
    wb = openpyxl.load_workbook(f, data_only=True, read_only=True)
    for ws in wb.worksheets:
        rows = []
        for row in ws.iter_rows(values_only=True):
            if row and isinstance(row[0], str) and isinstance(row[1], (int, float)) and isinstance(row[3], str) and isinstance(row[5], (int, float)):
                rows.append({"label": row[0], "pay": round(row[1] * 100), "cum": round(row[2] * 100), "code": row[3].strip(),
                             "w1m1": (row[4] or '').strip() if isinstance(row[4], str) else '', "period": int(row[5]),
                             "due": round(row[6] * 100), "todate": round(row[7] * 100)})
        if rows:
            out.write(json.dumps({"file": f.split('/')[-1], "sheet": ws.title, "rows": rows}) + "\n")
