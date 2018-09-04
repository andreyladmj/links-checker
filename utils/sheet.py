from openpyxl import Workbook

wb_result = Workbook(write_only=True)
ws_result = wb_result.create_sheet()

ws_result.column_dimensions['A'].width = 40
ws_result.column_dimensions['B'].width = 20
ws_result.column_dimensions['C'].width = 40
ws_result.column_dimensions['D'].width = 15
ws_result.column_dimensions['E'].width = 15
ws_result.column_dimensions['F'].width = 15