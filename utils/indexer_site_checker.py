import time

import grequests
from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QProgressBar
from urllib3 import HTTPConnectionPool

from check_links import save_result_report, check_links_in_the_workbook
from utils.link import Link
from utils.utils import iterate_by_batch


class IndexerSiteChecker(QtCore.QThread):
    pbar_signal = QtCore.pyqtSignal(int)
    download_signal = QtCore.pyqtSignal(list)
    log_signal = QtCore.pyqtSignal(str)
    response_signal = QtCore.pyqtSignal(object)
    exception_signal = QtCore.pyqtSignal(object)

    def __init__(self, number, parent):
        super().__init__()
        self.number = number
        self.qlabel = QLabel('Process: {}'.format(self.number), parent)
        self.qbar = QProgressBar(parent)
        self.qbar.setMaximum(100)
        self.qbar.setMinimum(0)
        self.links = []
        self.processed = 0
        self.total = 0
        self.pbar_signal.connect(self.qbar.setValue)
        self.queue = []
        self.results = []

        self.response_signal.connect(parent.sites_responses.append)
        self.exception_signal.connect(parent.exceptions.append)
        self.log_signal.connect(parent.log)

    def set_links(self, links):
        self.pbar_signal.emit(0)
        self.links = list(links)
        self.total = len(self.links)
        self.update_info()

    def set_queue(self, queue):
        self.queue = queue

    def update_info(self):
        self.qlabel.setText('Worker: {} (Processed {} of {})'.format(self.number, self.processed, self.total))
        self.pbar_signal.emit(self.processed / self.total * 100)

    def finish(self):
        self.processed = self.total
        self.update_info()

    def run(self):
        results = []

        batches = iterate_by_batch(self.links, 20, None)

        for batch in batches:
            for link in batch:
                if not link: continue

                site, referer = link

                headers = {'referer': referer,
                           'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
                results.append(grequests.get(site, headers=headers, hooks={'response': self.check_site_response}, timeout=3))

            self.results = grequests.map(results, exception_handler=self.exception_handler, size=16)

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

    def check_site_response(self, response, *args, **kwargs):
        # self.log_signal.emit('GET {}, Status: {}'.format(response.url, response.status_code))
        self.processed += 1
        self.update_info()

        # if response.status_code == 301:
        #     self.log_signal.emit('{} redirected to {}'.format(response.url, response.headers.get('Location')))

        self.response_signal.emit(response)
        return response

    def exception_handler(self, request, exception):
        self.processed += 1
        self.update_info()
        self.log_signal.emit("Site: {}; Exception: {}".format(request.url, exception))
        self.exception_signal.emit({'site': request.url, 'exception': exception})