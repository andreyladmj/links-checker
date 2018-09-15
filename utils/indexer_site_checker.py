import os
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
    plabel_signal = QtCore.pyqtSignal(str)


    log_signal = QtCore.pyqtSignal(str)
    response_signal = QtCore.pyqtSignal(object)
    exception_signal = QtCore.pyqtSignal(object)
    finish_signal = QtCore.pyqtSignal()


    # percent_log_signal = QtCore.pyqtSignal(int, str)

    def __init__(self, number, parent):
        super().__init__()
        self.number = number
        # self.qlabel = QLabel('Process: {}'.format(self.number), parent)
        # self.qbar = QProgressBar(parent)
        # self.qbar.setMaximum(100)
        # self.qbar.setMinimum(0)
        self.links = []
        self.processed = 0
        self.total = 0
        # self.pbar_signal.connect(self.qbar.setValue)
        self.queue = []
        self.results = []

        self.black_list = []

        self.response_signal.connect(parent.sites_responses.append)
        self.exception_signal.connect(parent.save_exception)
        self.log_signal.connect(parent.qlogs.log)
        self.finish_signal.connect(parent.finish)


        # self.percent_log_signal.connect(parent.qlogs.update_thread_info)

    def set_links(self, links):
        self.pbar_signal.emit(0)
        self.links = links
        self.processed = 0
        self.total = sum([link.count for link in links if link])
        self.update_info()

    def update_info(self):
        # self.qlabel.setText('Worker: {} (Processed {} of {})'.format(self.number, self.processed, self.total))
        self.pbar_signal.emit(self.processed / self.total * 100)
        self.plabel_signal.emit('Worker: {} (Processed {} of {})'.format(self.number, self.processed, self.total))
        # print(self.number, self.processed, self.total, int(self.processed / self.total * 100))
        # self.qbar.setValue(int(self.processed / self.total * 100))
        # self.log_signal.emit("Worker: {} - {}%, (Processed {} of {})".format(self.number, self.processed / self.total * 100, self.processed, self.total))

    def get_info(self):
        return "Worker: {} - {}%, (Processed {} of {})".format(self.number, self.processed / self.total * 100, self.processed, self.total)

    def set_bar_updating_bar_func(self, bar_fn, label_fn):
        self.pbar_signal.connect(bar_fn)
        self.plabel_signal.connect(label_fn)

    def finish(self):
        # self.processed = self.total
        self.update_info()
        self.log_signal.emit("Worker: {} is Finished!".format(self.number))
        self.finish_signal.emit()

    def run(self):
        can = True
        concurency = 20
        batch_size = concurency * 5

        while can:
            total_count = 0

            batches = iterate_by_batch(self.links, batch_size, None)

            for batch in batches:
                results = []

                for link in batch:
                    if not link: continue

                    site, referer, count = link.url, link.referer, link.count

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
                    # results.append(link)
                    # time.sleep(0.001)

                self.results = grequests.map(results, exception_handler=self.exception_handler, size=concurency)
                self.update_info()

            if not total_count:
                can = False

            print("Worker {}, Total count: {}, processed: {}".format(self.number, total_count, self.processed))

        self.finish()

    def check_site_response_decorator(self, spam_link):
        def check_site_response(response, *args, **kwargs):
            if response.is_redirect:
                self.total += 1

            self.processed += 1
            # self.update_info()
            return response

            spam_link.url = response.url
            spam_link.is_redirect = response.is_redirect
            spam_link.status_code = response.status_code
            spam_link.redirect_to = response.headers.get('Location')

            response.spam_link = spam_link
            #self.response_signal.emit(response)
            return response
        return check_site_response

    def exception_handler(self, request, exception):
        self.processed += 1
        self.black_list.append(request.url)
        # self.log_signal.emit("Site: {}; Exception: {}".format(request.url, exception))
        self.exception_signal.emit({'site': request.url, 'exception': exception})