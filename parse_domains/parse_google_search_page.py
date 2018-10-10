from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from utils.utils import read_file_lines

processed_domains = []
forbidden = read_file_lines('forbidden.txt')

def create_webdriver():

    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(
        # 'D:\projects\links-checker\chromedriver.exe',
        'chromedriver',
        service_args=['--disable-cache'],
        chrome_options=chrome_options)

def get_domain(link):
    n = link.find('/', 8)
    return link[:n]

def write_to_file(domains, filename):
    with open(filename, "a") as file:
        for link in domains:
            file.write("{}\n".format(link))

def search():
    links = driver.find_elements_by_tag_name('a')
    domains = []
    pages = []

    for link in links:
        if link.get_attribute('href') and 'http' in link.get_attribute('href'):
            domain = get_domain(link.get_attribute('href'))

            if domain not in forbidden and domain not in processed_domains:
                pages.append(link.get_attribute('href'))
                domains.append(domain)
                processed_domains.append(domain)

    print('Save {} domains'.format(len(domains)))
    write_to_file(domains, 'google_domains.txt')
    write_to_file(pages, 'google_pages.txt')

def get_next_page(n):
    links = driver.find_elements_by_tag_name('a')

    for link in links:
        if link.get_attribute('class') == 'fl' or link.get_attribute('class') == 'sb_bp':
            try:
                number = int(link.get_attribute('aria-label').replace('Page ', '').replace('Страница ', ''))

                if n == number:
                    print('get page', number)
                    return link
            except Exception:
                pass


# search_phrases = [
#     'wordpress leave comment students',
#     'wordpress replay',
#     'wordpress students',
#     'wordpress essay comment',
#     'wordpress graduate',
#     'wordpress university',
# ]

search_phrases = read_file_lines('/home/andrei/Python/links-checker/parse_domains/queries.txt')

if __name__ == '__main__':
    driver = create_webdriver()
    # driver.get("http://www.google.com")
    driver.get("https://www.bing.com")
    current = 0

    for sentence in search_phrases:
        current += 1
        print('Search {} of {} sentences'.format(current, len(search_phrases)))
        elem = driver.find_element_by_name("q")
        elem.clear()
        elem.send_keys("wp "+sentence)
        elem.send_keys(Keys.RETURN)

        for i in range(2, 10):
            search()
            page = get_next_page(i)
            if page:
                page.click()

    driver.close()