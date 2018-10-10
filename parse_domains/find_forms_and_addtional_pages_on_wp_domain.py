import grequests

from utils.utils import read_file_lines, iterate_by_batch, get_domain

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
pages = read_file_lines('google_pages.txt')
batch_size = 50
max_pages_with_form = 6

processed_domains = []
pages_with_forms = []

def response_callback(response, **kwargs):
    global processed_links, links_to_process, links_with_comments_form, total, current, processed_domains
    current += 1
    print('Got {} of {}'.format(current, total))

    domain = get_domain(response.url)

    if processed_domains.count(domain) > max_pages_with_form:
        return response

    text = response.text.lower()

    parsed_html = BeautifulSoup(text, "lxml")

    for a in parsed_html.body.find_all('a'):
        if a.get('href') and 'http' in a.get('href'):# and get_domain(a.get('href')) == domain:
            try_to_add_link_for_parsing(a.get('href'))

    if is_has_form(parsed_html.body.find_all('input')):
        pages_with_forms.append(response.url)
        processed_domains.append(domain)

    # for input in parsed_html.body.find_all('input'):
    #     if input.get('name') == 'comment_post_ID':
    #         links_with_comments_form.append(response.url)
    #         return
    #
    #     if input.get('name') == 'wpdiscuz_unique_id':
    #         links_with_comments_form.append(response.url)
    #         return
    #
    #     if input.get('name') == 'wc_email':
    #         links_with_comments_form.append(response.url)
    #         return

    return response

def is_has_form(inputs):
    for input in inputs:
        if input.get('name') == 'comment_post_ID':
            return True

        if input.get('name') == 'wpdiscuz_unique_id':
            return True

        if input.get('name') == 'wc_email':
            return True

    return False


def exception_handler(request, exception):
    print('Exception', request.url, exception)


def grequests_links(pages):
    for page in pages:
        if 'http' not in page:
            print('There are not http in {}'.format(page))
            continue

        grequest_stack.append(grequests.get(page, headers=headers,
                                            hooks={'response': response_callback},
                                            timeout=10))

if __name__ == '__main__':

    batches = iterate_by_batch(pages, batch_size, None)

    for pages in batches:
        grequest_stack = []
        grequests_links(pages)
        results = grequests.map(grequest_stack, exception_handler=exception_handler, size=20)
        print(results)
        raise Exception
