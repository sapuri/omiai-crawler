import argparse
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class OmiaiCrawler:
    def __init__(self, width: int = 1280, height: int = 960):
        options = webdriver.ChromeOptions()
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36')
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_size(width, height)

    def run(self, type: str = '', page_num: int = 1, timeout: int = 180):
        """
        :param type: <recommend | login | interests | fresh>
        :param page_num: number of loading pages
        :param timeout: timeout time for waiting for login (sec)
        """
        self.driver.get('https://www.omiai-jp.com/search')
        print('Waiting for login...')
        self.__wait_for_login(timeout)
        self.__select_search_menu(type)
        self.__close_info_dialog(type)
        self.__load_items(page_num)
        self.__crawl()
        time.sleep(10)
        self.driver.quit()
        print('Finished')

    def __wait_for_login(self, timeout: int = 180):
        try:
            WebDriverWait(
                self.driver, timeout).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, 'search-list-item')))
        except TimeoutException:
            print('Timeout')
            self.driver.quit()
            quit(1)

    def __load_items(self, page_num: int = 1):
        for _ in range(1, page_num):
            self.__page_down()
            time.sleep(1)
        self.__page_up()
        time.sleep(1)

    def __page_up(self):
        self.driver.execute_script("window.scrollTo(0, 0);")

    def __page_down(self):
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

    def __select_search_menu(self, type: str = ''):
        if type == 'fresh':
            self.driver.find_element_by_class_name(
                'om-button-search-menu').click()
            menu_id = 'om-search-menu-fresh'
            menu = self.driver.find_element_by_id(menu_id)
            menu.find_element_by_class_name('content').click()
            time.sleep(1)

    def __close_info_dialog(self, type: str = ''):
        if type == 'fresh':
            self.driver.find_element_by_id(
                'om-dialog-fresh-information-close').click()

    def __crawl(self):
        for i, item in enumerate(
                self.driver.find_elements_by_class_name('search-list-item')):
            print(f'#{i + 1}', item.get_attribute('data-nickname'))
            item.click()
            time.sleep(0.3)
            self.driver.back()
            time.sleep(0.7)


def load_args():
    parser = argparse.ArgumentParser(
        description='Omiai Crawler: A web crawler for Omiai with ChromeDriver')
    parser.add_argument(
        '-w',
        '--width',
        default=1280,
        help='width of the Chrome window')
    parser.add_argument(
        '-ht',
        '--height',
        default=960,
        help='height of the Chrome window')
    parser.add_argument(
        '-t',
        '--type',
        default='',
        help='<recommend | login | interests | fresh>')
    parser.add_argument(
        '-n',
        '--page_num',
        default=5,
        help='number of loading pages')
    parser.add_argument(
        '-tmo',
        '--timeout',
        default=180,
        help='timeout time for waiting for login (sec)')
    return parser.parse_args()


if __name__ == '__main__':
    args = load_args()
    crawler = OmiaiCrawler(width=args.width, height=args.height)
    try:
        crawler.run(
            type=args.type,
            page_num=args.page_num,
            timeout=args.timeout)
    except KeyboardInterrupt:
        quit(0)
