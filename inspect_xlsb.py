from pyxlsb import open_workbook

file_path = "data/raw/nwau25_calculator_for_ED_activity_AECC.xlsb"
try:
    with open_workbook(file_path) as wb:
        print(f"Sheets in {file_path}: {wb.sheets}")
        for sheet_name in wb.sheets:
            print(f"\nChecking sheet: {sheet_name}")
            with wb.get_sheet(sheet_name) as sheet:
                for row in sheet.rows():
                    for cell in row:
                        if (
                            cell.v
                            and isinstance(cell.v, str)
                            and ("NEP" in cell.v or "Price" in cell.v)
                        ):
                            print(f"Found match: '{cell.v}' at row {cell.r}, col {cell.c}")
                        # Also look for the known 2025 value 7258
                        if cell.v and (cell.v == 7258 or cell.v == 7258.0):
                            print(f"Found value 7258 at row {cell.r}, col {cell.c}")
except Exception as e:
    print(f"Error: {e}")
