from urllib.request import urlopen

import requests
from openpyxl import load_workbook
import urllib
from lxml import html

import urllib

def check_site(url, text='', link=''):
    page = requests.get(url)
    tree = html.fromstring(page.content)
    print(page)

if __name__ == '__main__':

    wb = load_workbook('college_papers_for_sale.xlsx')
    ws = wb.active

    for column in ws.iter_rows():
        acceptor = column[0]
        anchor = column[1]
        donor = column[2]

        if 'http' in acceptor.value:
            print(acceptor.value, anchor.value, donor.value)
            check_site(acceptor.value)
            print('-----')

