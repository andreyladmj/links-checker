import grequests
from openpyxl import load_workbook

from utils.utils import save_pickle, load_pickle, read_file_lines

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}

google_start_page = "https://www.google.com.ua/search?q=wordpress+leave+comment+students&ei=dGC8W8GBNIO4sQG0to64CQ&start={}&sa=N&biw=1307&bih=395"

start_pages = [
    'https://unlocktheteacher.wordpress.com/2012/07/22/100-positive-comments-to-utilize-when-speaking-on-students-behaviorr/'
]


# for i in range(20, 80, 10):
#     start_pages.append(google_start_page.format(i))


tmp_file = 'domains.pkl'

processed_domains = []
processed_links = []
links_to_process = []
links_with_comments_form = []
forbidden = read_file_lines('forbidden.txt')

total = 0
current = 0

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup


def response_callback(response, **kwargs):
    global processed_links, links_to_process, links_with_comments_form, total, current, processed_domains
    current += 1
    print('Got {} of {}'.format(current, total))

    if current and current % 500 == 0:
        save_data()

    processed_links.append(response.url)

    text = response.text.lower()

    parsed_html = BeautifulSoup(text, "lxml")

    for a in parsed_html.body.find_all('a'):
        href = a.get('href')
        print(href)

        if not href: continue

        domain = get_domain(href)

        if 'http' in domain and domain not in processed_domains and domain not in forbidden:
            processed_domains.append(domain)
            links_to_process.append(domain)
    raise Exception
    return response


def exception_handler(request, exception):
    global current
    current += 1
    print('Exception', request.url, exception)



def get_domain(link):
    n = link.find('/', 8)
    return link[:n]

def grequests_links():
    global links_to_process, grequest_stack, total

    print('get pages links_to_process', len(links_to_process))
    total = len(links_to_process)

    for i in range(len(links_to_process)):
        link = links_to_process.pop()

        if 'http' not in link:
            print('There are not http in {}'.format(link))
            continue

        grequest_stack.append(grequests.get(link, headers=headers,
                                            hooks={'response': response_callback},
                                            timeout=10))


def save_data():
    global processed_links, links_to_process, links_with_comments_form, processed_domains
    stage = {
        'processed_links': processed_links,
        'links_to_process': links_to_process,
        'links_with_comments_form': links_with_comments_form,
        'processed_domains': processed_domains,
    }
    print("Saved Data, links_with_comments_form: {}, processed_links: {}, links_to_process: {}, processed_domains: {}".format(
        len(links_with_comments_form), len(processed_links), len(links_to_process), len(processed_domains)))
    save_pickle(tmp_file, stage)

    with open('domains.txt', 'w') as file:
        for link in processed_domains:
            file.write("{}\n".format(link))


if __name__ == '__main__':
    links_to_process += start_pages
    grequest_stack = []

    try:
        data = load_pickle(tmp_file)
        processed_links = data['processed_links']
        links_to_process = data['links_to_process']
        links_with_comments_form = data['links_with_comments_form']
        processed_domains = data['processed_domains']
    except Exception:
        pass

    while len(links_to_process):
        grequests_links()

        results = grequests.map(grequest_stack, exception_handler=exception_handler, size=20)

        save_data()
