import json
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_cookies():
    chrome_options = Options()
    # 设置headless模式
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    # 设置不加载图片
    # chrome_options.add_argument('blink-settings=imagesEnabled=false')
    browser = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver", options=chrome_options)
    #
    # browser.get(url='https://www.douban.com')
    # time.sleep(2)
    # browser.switch_to.frame(browser.find_element_by_xpath('//div[@id="anony-reg-new"]//div[@class="wrapper"]/div[@class="login"]/iframe'))
    # browser.find_element_by_xpath('//li[@class="account-tab-account"]').click()
    # username = browser.find_element_by_xpath('//input[@id="username"]')
    # username.clear()
    # username.send_keys('xinkucheng@163.com')
    # time.sleep(1.2)
    # password = browser.find_element_by_xpath('//input[@id="password"]')
    # password.clear()
    # password.send_keys('xinyuanchang13')
    # time.sleep(1)
    # remember = browser.find_element_by_xpath('//input[@id="account-form-remember"]')
    # remember.click()
    # time.sleep(1)
    # btn_login = browser.find_element_by_xpath('//div[@class="account-tabcon-start"]//div[@class="account-form-field-submit "]/a')
    # btn_login.click()
    # time.sleep(5)
    # cookies_str = browser.get_cookies()
    cookies_str = 'll="108288"; bid=2CgiqpTdjb8; _pk_ses.100001.8cb4=*; __utma=30149280.409180215.1574271343.1574271343.1574271343.1; __utmc=30149280; __utmz=30149280.1574271343.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1; dbcl2="51476394:++j1PWRmpmU"; ck=sD9U; _pk_id.100001.8cb4=1f685a44658a537c.1574271342.1.1574271373.1574271342.; ap_v=0,6.0; __gads=Test; __yadk_uid=SpdgSw9uXVamo2ByLE8U2xX6K4LncoeW; push_noty_num=0; push_doumail_num=0; __utmv=30149280.5147; __utmb=30149280.4.10.1574271343'
    # 格式化cookies
    cookie_dict_list = parse_cookies(cookies_str)
    # 保存本地
    with open("cookies_selenium.txt", 'w') as fw:
        fw.write(json.dumps(cookie_dict_list))
    # 从本地读取
    with open("cookies_selenium.txt", 'r') as fr:
        cookies = json.loads(fr.read())

    # 先打开网站，再添加cookies，否则报错domain无效
    response = browser.get(url='https://www.douban.com')
    for cookie_dict in cookie_dict_list:
        print(cookie_dict)
        browser.add_cookie(cookie_dict)
    response = browser.get(url='https://www.douban.com')

    if "不肖生" in browser.page_source:
        print("success")

def parse_cookies(cookie_str):
    # 格式化cookies为字典列表
    cookie_list = cookie_str.split('; ')
    cookies = []
    for cookie in cookie_list:
        cook_list = cookie.split('=')
        cookie_dict = {
            'name': cook_list[0],
            'value': cook_list[1],
            # chrome要求domain，火狐不要
            'domain':'.douban.com'
        }
        if 'yadk' in cook_list[0] or '_pk_' in cook_list[0]:
            cookie_dict['domain'] = 'www.douban.com'
        cookies.append(cookie_dict)
    return cookies

def read_cookies():
    with open('cookies.txt','r') as f:
        cookies_str = json.loads(f.read())
    return cookies_str

if __name__ == "__main__":
    get_cookies()
    # cookies = read_cookies()
    # print(cookies)

