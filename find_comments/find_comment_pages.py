import grequests
from openpyxl import load_workbook

from utils.utils import save_pickle, load_pickle

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}

start_pages = [
    # 'https://www.google.com.ua/search?q=wordpress+leave+comment&ei=REe8W8e6N4GOsAGtl4L4CA&start=60&sa=N&biw=1867&bih=951' # 7
    # 'https://larryferlazzo.edublogs.org/2018/10/08/video-does-using-your-phone-really-hurt-your-sleep/'
    'https://www.google.com.ua/search?q=wordpress+leave+comment&ei=I2C8W_XLH42SmgWB073wCA&start=80&sa=N&biw=1307&bih=395',
    'https://www.google.com.ua/search?q=wordpress+leave+comment+students&ei=dGC8W8GBNIO4sQG0to64CQ&start=50&sa=N&biw=1307&bih=395',
    'https://www.google.com.ua/search?q=wordpress+leave+comment+students&ei=j2C8W8HHI4mmsgG787GIDA&start=60&sa=N&biw=1307&bih=395',
    'https://help.edublogs.org/read-student-posts/',
    'https://alliedstrategiespodcast.wordpress.com/2018/09/06/episode-153-guilds-of-ravnica-mechanics/comment-page-1/#comment-507',
    'https://commercialsociety.wordpress.com/2018/10/06/mentos-gum-says-to-small-talk-it/',
    'https://handsonwp.com/headless-woocommerce/',
    'https://wphowto.net/how-to-add-a-free-ssl-certificate-to-your-wordpress-site-3787',
    'https://mysterythemes.com/blog/methods-to-solve-redirects-issue-in-wordpress/',
    'https://www.wpeka.com/wordpress-interactive-site-plugins.html',
    'https://napitwptech.com/tutorial/wordpress-development/create-shortcode-with-attributes-wordpress/',
    'https://writersforensicsblog.wordpress.com/2018/10/08/does-your-dna-contain-your-image/',
    'https://fanningsessions.wordpress.com/2018/10/08/woodstar-2002-session/',
]

processed_domains = []
processed_links = []
links_to_process = []
links_with_comments_form = []

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
    processed_domains.append(get_domain(response.url))

    text = response.text.lower()

    parsed_html = BeautifulSoup(text, "lxml")

    for a in parsed_html.body.find_all('a'):
        try_to_add_link_for_parsing(a.get('href'))

    if get_domain(response.url) in processed_domains:
        return

    for input in parsed_html.body.find_all('input'):
        if input.get('name') == 'comment_post_ID':
            links_with_comments_form.append(response.url)
            return

        if input.get('name') == 'wpdiscuz_unique_id':
            links_with_comments_form.append(response.url)
            return

        if input.get('name') == 'wc_email':
            links_with_comments_form.append(response.url)
            return

    return response


def exception_handler(request, exception):
    global current
    current += 1
    print('Exception', request.url, exception)


def try_to_add_link_for_parsing(link):
    global links_to_process, processed_links

    if not link: return
    if link in processed_links: return
    if 'http' not in link: return
    if 'google.com' in link: return
    if 'cloudflare.com' in link: return
    if 'youtube.com' in link: return
    if 'instagram.com' in link: return
    if 'pinterest.com' in link: return
    if 'facebook.com' in link: return
    if 'twitter.com' in link: return
    if 't.co/' in link: return
    if 'wordpress.org' in link: return
    if 'www.amazon.com' in link: return
    if 'www.tumblr.com' in link: return
    if 'yahoo.com' in link: return
    if 'whatsapp.com' in link: return

    links_to_process.append(link)


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
    save_pickle('find_comments.pkl', stage)


if __name__ == '__main__':
    links_to_process += start_pages
    grequest_stack = []

    try:
        data = load_pickle('find_comments.pkl')
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
