from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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
    # url = 'http://ryanbradley.com/blog/service-area-businesses-gmb-schema-setup'
    # url = 'https://barn2.co.uk/wordpress-comments-page-post-widget/'
    # url = 'https://colorlib.com/wp/free-resume-templates/'
    url = 'https://embedds.com/gadgets-that-can-help-you-with-training-your-body/'
    # url = 'http://thegameofthrones.co/september-2017-printable-calendar-templates/'
    browser = create_webdriver()
    browser.get(url)

    type_to_field_name(browser, "comment", "I like it !!")
    type_to_field_name(browser, "author", "Udel Baranov")
    type_to_field_name(browser, "email", "otjer.mamonov@gmail.com")
    type_to_field_name(browser, "url", "tri-dnya-v-zapoe.com")
    submit = browser.find_element_by_name('submit')
    submit.click()

    #print(el.find_element_by_xpath(".."), str(el.find_element_by_xpath("..")))

    #browser.close()