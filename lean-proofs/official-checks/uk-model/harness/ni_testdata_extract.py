"""Extract HMRC 2025-26 NIC test data rows (employee column) to JSONL: freq, cat, pay (pence), employee (pence)."""
import sys, json, openpyxl
wb = openpyxl.load_workbook(sys.argv[1], data_only=True, read_only=True)
out = open(sys.argv[2], 'w')
for ws in wb.worksheets:
    for row in ws.iter_rows(values_only=True):
        if row and isinstance(row[0], str) and isinstance(row[1], (int, float)) and isinstance(row[3], str):
            out.write(json.dumps({"sheet": ws.title, "freq": row[0], "pay": round(row[1] * 100), "cat": row[3],
                                  "employee": round(row[4] * 100), "employer": round(row[5] * 100)}) + "\n")
