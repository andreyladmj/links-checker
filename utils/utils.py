import time
from itertools import zip_longest

from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Font


def iterate_by_batch(array_list, amount, fillvalue=None):
    args = [iter(array_list)] * amount
    return zip_longest(*args, fillvalue=fillvalue)


def read_file(file):
    with open(file, 'r') as f:
        read_data = f.read()
    return read_data


def make_xlsx_file(fileName, head=None, body=None):
    def make_cell(value, size=9, bold=False):
        cell = WriteOnlyCell(ws, value=value)
        cell.font = Font(name='Verdana', size=size, bold=bold)
        return cell

    wb = Workbook(write_only=True)
    ws = wb.create_sheet()

    ws.column_dimensions['A'].width = 40
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 40
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 15
    ws.column_dimensions['F'].width = 15

    if head:
        head = [make_cell(title, bold=True) for title in head]
        ws.append(head)

    if body:
        for row in body:
            row_cells = [make_cell(col) if not isinstance(col, type(WriteOnlyCell)) else col for col in row]
            ws.append(row_cells)

    wb.save(fileName)
