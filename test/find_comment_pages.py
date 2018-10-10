import grequests
from openpyxl import load_workbook

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}

start_pages = [
    # 'https://www.google.com.ua/search?q=wordpress+leave+comment&ei=REe8W8e6N4GOsAGtl4L4CA&start=60&sa=N&biw=1867&bih=951' # 7
    'https://larryferlazzo.edublogs.org/2018/10/08/video-does-using-your-phone-really-hurt-your-sleep/'
]

processed_links = []
links_to_process = []
links_with_comments_form = []

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

def response_callback(response, **kwargs):
    global processed_links, links_to_process
    processed_links.append(response.url)

    text = response.text.lower()

    parsed_html = BeautifulSoup(text, "lxml")

    for a in parsed_html.body.find_all('a'):
        try_to_add_link_for_parsing(a.get('href'))

    for input in parsed_html.body.find_all('input'):
        print(input)

    return response


def exception_handler(request, exception):
    print('Exception', request.url, exception)


def try_to_add_link_for_parsing(link):
    global links_to_process, processed_links

    if link in processed_links: return
    if 'google.com' in link: return
    if 'cloudflare.com' in link: return
    if 'youtube.com' in link: return
    if 'instagram.com' in link: return
    if 'pinterest.com' in link: return
    if 'facebook.com' in link: return
    if 'http://www.wordpress.org' in link: return



if __name__ == '__main__':
    links_to_process += start_pages
    grequest_stack = []

    for link in links_to_process:
        if 'http' not in link:
            print('There are not http in {}'.format(link))
            continue

        grequest_stack.append(grequests.get(link, headers=headers,
                                            hooks={'response': response_callback},
                                            timeout=10))

    results = grequests.map(grequest_stack, exception_handler=exception_handler, size=16)
