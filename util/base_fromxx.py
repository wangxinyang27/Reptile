import time
import warnings
from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import trange
from time import sleep
from random import randint
warnings.filterwarnings("ignore", category=DeprecationWarning)


class BaseCatch(object):
    """Derived classes for all relevant functionality inherit from this class"""
    # please use firefox
    def __init__(self, url_name, type_):
        # Do not start the browser

        fp = webdriver.FirefoxProfile()
        # Limit CSS loading
        fp.set_preference("permissions.default.stylesheet", 2)
        # Limit image loading
        fp.set_preference('permissions.default.image', 2)
        # Restrict JavaScript execution
        fp.set_preference('javascript.enabled', False)
        Firefoxoptions = webdriver.FirefoxOptions()
        # windowless mode
        Firefoxoptions.add_argument('--headless')
        Firefoxoptions.add_argument('--disable-gpu')
        Firefoxoptions.add_argument('window-size=1200x600')

        # browser = webdriver.Firefox(executable_path='/home/wxy/下载/geckodriver-v0.31.0-linux64/geckodriver')
        browser = webdriver.Firefox(executable_path='/home/wxy/下载/geckodriver-v0.31.0-linux64/geckodriver', options=Firefoxoptions, firefox_profile=fp)
        self.url_dir = {
            'bilibili': 'https://www.bilibili.com/',
            'bilibili_read': 'https://www.bilibili.com/read/',  # Bilibili article URL
            'bilibili_video': 'https://www.bilibili.com/video/', # Bilibili video URL
            'green_application': 'https://www.dongqiudi.com/',  # Green application URL
            'baidu_tieba': 'https://tieba.baidu.com/' # BaiduTieba URL
        }
        self.url_name = url_name
        self.type_ = type_
        self.browser = browser
        self.download_path = []
        self.now = None

    def _get_code_frompage(self, URL):
        self.browser.get(URL)
        time.sleep(5)
        self.data = self.browser.page_source
        soup = BeautifulSoup(self.data, 'lxml')
        if soup.title.string == '什么都没找到':
            raise NameError("There seems to be an error with the webpage you are trying to access, "
                            "please check your bv number and try again.")

    def _extract_fromcode(self, show_inf=False):
        pass

    def _check_downloadpath(self, print_=False):
        pass

    @staticmethod
    def _print_download_path():
        # we had finished its function in other
        pass

    def download(self, time_side=0.5):
        pass

    def notes(self):
        pass

    @staticmethod
    def Procession(label, speed, total=100):
        # It only plays a decorative role, and does not correctly reflect the download speed......
        with trange(total) as t:
            for i in t:
                t.set_description('{} Processing:'.format(label))
                t.set_postfix(gen=randint(100, 999), format='None')

                sleep(0.1 * randint(speed[0], speed[1]))

