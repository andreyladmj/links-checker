from utils.selenium_checker import SeleniumChecker
from utils.utils import read_file_lines, create_selenium_dict_for_form

if __name__ == '__main__':
    count = 0
    donors = read_file_lines('/home/andrei/Python/links-checker/wp/donors.txt')
    Comment = SeleniumChecker()


    for donor in donors:
        url = donor
        count += 1

        if count < 260: continue

        try:
            Comment.get(url)
            print('Get {}, #{} of {}'.format(url, count, len(donors)))

            if not Comment.find_form():
                print('Form not Found on {}'.format(donor))

            else:
                comment = 'learners can find support with essays'
                author = 'Isabella Arnold'
                email = 'warrenjt1978@yahoo.com'
                acceptor = 'http://www.londonjobsfinder.com/author/audrey-j-hayter'
                params = create_selenium_dict_for_form(acceptor=acceptor, comment=comment, author=author, email=email)

                data = Comment.post_comment(**params)
                Comment.save_screenshot(url)

                print("Fields")
                print(Comment.get_form_fields())
                print('Data:')
                print(data)
                print("\n\n")
        except Exception as e:
            print('Exception on {}, {}'.format(url, str(e)))
            print("\n\n")