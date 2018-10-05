from random import shuffle
from time import time

from utils.cycled_iterator import CycledIterator
from utils.utils import iterate_by_batch, make_xlsx_file, read_file, read_file_lines
from widgets.components.comments import QComments

'''
Исходные данные:
Есть база с донорами URL страницы: donors.txt
Есть база акцепторов, текст для заполнения поля Website : acceptors.txt
Есть текст для заполнения поля Name: UserName.txt
Есть текст для заполнения поля Email: Mail.txt
Есть текст для заполнения поля Comment: TextComment.txt

Система такая: 

Нужно на странице донора заполнить поля:

Website из файла acceptors.txt 
Name из файла UserName.txt  
Email из файла Mail.txt  
Comment из файла TextComment.txt  

И отправить на сабмит кнопкой: Post Comment
'''


class TestComments():

    def __init__(self):
        self.title = 'WP Comments'

        self.acceptors_file = '../wp/acceptors.txt'
        self.donors_file = '../wp/donors.txt'
        self.mails_file = '../wp/Mail.txt'
        self.text_comments_file = '../wp/TextComment.txt'
        self.user_names_file = '../wp/UserName.txt'

        self.acceptors = []
        self.donors = []
        self.mails = []
        self.text_comments = []
        self.user_names = []

    def start_comment(self):
        self.start_time = time()
        self.read_files()

        acceptors = CycledIterator(self.acceptors)

        Comment = QComments(1)
        Comment.set_donors(self.donors)
        Comment.set_acceptors(acceptors.get_batch(len(self.donors)))
        Comment.set_emails(self.mails)
        Comment.set_comments(self.text_comments)
        Comment.set_usernames(self.user_names)
        Comment.try_to_recover()
        Comment.donors_loop(self.donors)
        # Comment.start()
        # print('Make report')
        # self.make_report(Comment.processed_sites)
        print('Make Errors report')
        self.make_error_report(Comment.processed_sites)

    def read_files(self):
        self.acceptors = read_file_lines(self.acceptors_file)
        self.donors = list(filter(lambda x: x.strip(), read_file_lines(self.donors_file)))
        self.mails = read_file_lines(self.mails_file)
        self.text_comments = read_file_lines(self.text_comments_file)
        self.user_names = read_file_lines(self.user_names_file)

        self.acceptors = list(map(lambda x: x.strip(), self.acceptors))
        self.mails = list(map(lambda x: x.strip(), self.mails))
        self.text_comments = list(map(lambda x: x.strip(), self.text_comments))
        self.user_names = list(map(lambda x: x.strip(), self.user_names))

        shuffle(self.mails)

    def make_report(self, commented_sites):
        data = []
        name = 'report.xlsx'

        for site in commented_sites:
            if not site['success']: continue
            data.append([
                site['donor'].strip(),
                site['acceptor'].strip(),
                site['email'].strip(),
                site['author'].strip(),
                site['comment'].strip(),
                site['screenshot_before'].strip(),
                site['screenshot_after'].strip(),
            ])

        column_dimensions = {
            'A': {'width': 60, 'height': 50},
            'B': {'width': 60, 'height': 20},
            'C': {'width': 30, 'height': 20},
            'D': {'width': 30, 'height': 20},
            'E': {'width': 60, 'height': 20},
            'F': {'width': 60, 'height': 20},
        }

        make_xlsx_file(name, head=['Donor', 'Acceptor', 'Email', 'Author', 'Comment', 'Screenshot Before', 'Screenshot After'], body=data,
                       column_dimensions=column_dimensions)
        print('Report saved to {}!'.format(name))

    def make_error_report(self, sites):
        data = []
        name = 'error_report.xlsx'

        for site in sites:
            if site['success']: continue

            data.append([
                site['donor'].strip(),
                site['error'].strip(),
            ])

        column_dimensions = {
            'A': {'width': 60, 'height': 20},
            'B': {'width': 60, 'height': 20},
        }

        make_xlsx_file(name, head=['Donor', 'Error'], body=data, column_dimensions=column_dimensions)
        print('Error Report saved to {}!'.format(name))


if __name__ == '__main__':
    c = TestComments()
    c.start_comment()
