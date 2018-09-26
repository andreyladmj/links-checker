import time

import grequests
from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QProgressBar

from check_links import save_result_report, check_links_in_the_workbook
from utils.link import Link
from utils.proccess_bar_thread import ProccessBarThread


class ParseXLSX(ProccessBarThread):

    def __init__(self, number, parent):
        super().__init__()
        self.number = number
        self.links = []
        self.processed = 0
        self.total = 0
        self.queue = []
        self.results = []

        self.finish_signal.connect(parent.finish)

    def set_links(self, links):
        self.pbar_signal.emit(0)
        self.links = list(links)
        self.total = len(self.links)
        self.update_info()

    def run(self):
        results = []

        for link in self.links:
            if not link:
                self.processed += 1
                continue

            acceptor = link[0].value
            anchor = link[1].value
            donor = link[2].value

            if not acceptor or not donor or 'http' not in acceptor or 'http' not in donor: continue

            headers = {
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
            results.append(grequests.get(donor, headers=headers,
                                         hooks={'response': self.check_acceptor_decorator(acceptor, anchor, donor)}))

        self.results = grequests.map(results, exception_handler=self.exception_handler, size=16, gtimeout=12)

        self.finish()

    def check_acceptor_decorator(self, acceptor, anchor, donor):
        def check_acceptor(response, *args, **kwargs):
            link = Link(acceptor, anchor, donor)
            link.check(response.text, response.status_code)
            response.link = link

            self.log_signal.emit('Thread {}: checked {} in {} - {}'.format(self.number, acceptor, donor, link.has_acceptor))
            self.processed += 1
            self.update_info()

            return response

        return check_acceptor

    def exception_handler(self, request, exception):
        self.processed += 1
        self.exception_signal.emit({'site': request.url, 'exception': exception})