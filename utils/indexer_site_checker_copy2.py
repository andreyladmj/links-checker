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
    log_signal = QtCore.pyqtSignal(str)
    response_signal = QtCore.pyqtSignal(object)
    exception_signal = QtCore.pyqtSignal(object)
    finish_signal = QtCore.pyqtSignal()

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

        self.black_list = []

        self.response_signal.connect(parent.sites_responses.append)
        self.exception_signal.connect(parent.exceptions.append)
        self.log_signal.connect(parent.log)
        self.finish_signal.connect(parent.finish)

    def set_links(self, links):
        self.pbar_signal.emit(0)
        self.links = links
        self.total = sum([link.count for link in links if link])
        self.update_info()

    def update_info(self):
        self.qlabel.setText('Worker: {} (Processed {} of {})'.format(self.number, self.processed, self.total))
        self.pbar_signal.emit(self.processed / self.total * 100)

    def finish(self):
        self.processed = self.total
        self.update_info()
        self.finish_signal.emit()

    def run(self):
        results = []
        can = True

        while can:
            total_count = 0

            for link in self.links:
                if not link: continue

                site, referer, count = link.url, link.referer, link.count
                print(site, referer, count)

                if not count: continue

                link.count -= 1

                total_count += link.count

                if site in self.black_list:
                    self.processed += 1
                    self.update_info()
                    continue

                headers = {'referer': referer,
                           'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
                results.append(grequests.get(site, headers=headers, hooks={'response': self.check_site_response_decorator(link)}, timeout=10))

            self.results = grequests.map(results, exception_handler=self.exception_handler, size=16)

            if not total_count:
                can = False

        self.finish()

    def check_site_response_decorator(self, spam_link):
        def check_site_response(response, *args, **kwargs):
            self.processed += 1
            self.update_info()
            response.spam_link = spam_link
            self.response_signal.emit(response)
            return response
        return check_site_response

    def exception_handler(self, request, exception):
        self.processed += 1
        self.update_info()
        self.black_list.append(request.url)
        # self.log_signal.emit("Site: {}; Exception: {}".format(request.url, exception))
        self.exception_signal.emit({'site': request.url, 'exception': exception})