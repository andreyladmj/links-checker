import pickle
import time
from itertools import zip_longest

import grequests
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


def read_file_lines(file):
    with open(file) as f:
        return list(map(lambda x: x.strip(), f.readlines()))


def make_xlsx_file(fileName, head=None, body=None, column_dimensions=None):
    def make_cell(value, size=9, bold=False):
        cell = WriteOnlyCell(ws, value=value)
        cell.font = Font(name='Verdana', size=size, bold=bold)
        return cell

    wb = Workbook(write_only=True)
    ws = wb.create_sheet()

    if column_dimensions:
        for k, v in column_dimensions.items():
            for param, value in v.items():
                setattr(ws.column_dimensions[k], param, value)
    else:
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


def create_selenium_dict_for_form(acceptor, comment, author, email):
    acceptor = acceptor.strip()
    comment = comment.strip()
    author = author.strip()
    email = email.strip()

    return {
        'comment': comment,
        'wc_comment': comment,

        'url': acceptor,
        'wc_website': acceptor,

        'author': author,
        'wc_name': author,

        'mail': email,
        'email': email,
        'wc_email': email,
    }


def get_simple_page(url, callback):
    headers = {
        'referer': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}

    results = grequests.map([
        grequests.get(url, headers=headers, hooks={'response': callback}, timeout=10)
    ], exception_handler=lambda request, exception: print('Exception!', request, exception), size=16)


def save_pickle(name, data):
    with open(name, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load_pickle(name):
    with open(name, 'rb') as handle:
        return pickle.load(handle)


def append_pickle(name, data):
    data = data + load_pickle(name)
    save_pickle(name, data)

def get_domain(link):
    n = link.find('/', 8)
    return link[:n]