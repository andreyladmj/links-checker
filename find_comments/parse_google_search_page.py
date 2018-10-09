from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from utils.utils import read_file_lines

processed_domains = []
forbidden = read_file_lines('forbidden.txt')
forbidden = list(map(lambda x: x.strip(), forbidden))

def create_webdriver():

    chrome_options = Options()
    #chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(
        'D:\projects\links-checker\chromedriver.exe',
        # 'chromedriver',
        service_args=['--disable-cache'],
        chrome_options=chrome_options)

def get_domain(link):
    n = link.find('/', 8)
    return link[:n]

def write_to_file(processed_domains):
    with open('google_domains.txt', 'w') as file:
        for link in processed_domains:
            file.write("{}\n".format(link))

def search():
    links = driver.find_elements_by_tag_name('a')
    domains = []

    for link in links:
        if link.get_attribute('href') and 'http' in link.get_attribute('href'):
            domain = get_domain(link.get_attribute('href'))

            if domain not in forbidden and domain not in processed_domains:
                print('domain', domain)
                domains.append(domain)
                processed_domains.append(domain)

    write_to_file(domains)

def get_next_page(n):
    links = driver.find_elements_by_tag_name('a')

    for link in links:
        if link.get_attribute('class') == 'fl':
            try:
                number = int(link.get_attribute('aria-label').replace('Page ', ''))

                if n == number:
                    print('get number', number)
                    return link
            except Exception:
                pass

search_phrases = [
    'wordpress leave comment students',
    'wordpress replay',
]

if __name__ == '__main__':
    driver = create_webdriver()
    driver.get("http://www.google.com")
    elem = driver.find_element_by_name("q")

    for sentence in search_phrases:
        elem.send_keys(sentence)
        elem.send_keys(Keys.RETURN)

        for i in range(2, 9):
            search()
            page = get_next_page(i)
            if page:
                page.click()

    driver.close()