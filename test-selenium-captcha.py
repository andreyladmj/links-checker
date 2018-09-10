import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


def create_webdriver():
    chrome_options = Options()
    #chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(
        '/home/andrei/Documents/fof/yana/chromedriver',
        service_args=['--disable-cache'],
        chrome_options=chrome_options)

def type_to_field_name(browser, name, message):
    comment = browser.find_element_by_name(name)
    comment.clear()
    comment.send_keys(message)


# try to find by form

if __name__ == '__main__':
    url = 'https://blogs.canterbury.ac.nz/intercom/2018/05/16/student-first-the-technology-story-open-information-session-with-guest-speakers/'
    browser = create_webdriver()
    #browser.get(url)

    #browser.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')
    browser.get('http://gmail.com')
    #type_to_field_name(browser, "identifier", "andrey.ladmj@gmail.com")
    browser.find_element_by_name("identifier").send_keys('andrey.ladmj@gmail.com' + Keys.ENTER)
    time.sleep(3)
    browser.find_element_by_name("password").send_keys('Andrey77701' + Keys.ENTER)
    time.sleep(5)
    browser.get(url)
    browser.find_element_by_id('recaptcha-anchor').click()
    time.sleep(3)

    #browser.pre
    # type_to_field_name(browser, "comment", "I like it !!")
    # type_to_field_name(browser, "author", "Udel Baranov")
    # type_to_field_name(browser, "email", "otjer.mamonov@gmail.com")
    # type_to_field_name(browser, "url", "tri-dnya-v-zapoe.com")
    # submit = browser.find_element_by_name('submit')
    # submit.click()

    #print(el.find_element_by_xpath(".."), str(el.find_element_by_xpath("..")))

    #browser.close()