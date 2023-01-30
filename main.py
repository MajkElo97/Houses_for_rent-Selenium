from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep
from os.path import exists

CHROME_DRIVER_PATH = 'C:\Development\chromedriver.exe'
FORM = 'https://docs.google.com/forms/d/e/1FAIpQLSdoUKDoZPY7tJ9AlHs2FOOKzawonUFBEqFOlXW3IPF_rWPtVw/viewform?usp=sf_link'
RENT_URL = 'https://www.zillow.com/homes/for_rent/1-_beds/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3Anull%2C%22mapBounds%22%3A%7B%22west%22%3A-122.56276167822266%2C%22east%22%3A-122.30389632177734%2C%22south%22%3A37.69261345230467%2C%22north%22%3A37.857877098316834%7D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22pmf%22%3A%7B%22value%22%3Afalse%7D%2C%22pf%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A3000%7D%2C%22price%22%3A%7B%22max%22%3A872627%7D%2C%22beds%22%3A%7B%22min%22%3A1%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A12%7D'
RENT_URL_STATIC = 'https://www.zillow.com'


# HEADER = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
#     "Accept-Language": "pl,pl-PL;q=0.9,en-US;q=0.8,en;q=0.7"
# }


class RentFinder:
    def __init__(self, path):
        self.prices_formatted = []
        self.links_formatted = []
        self.results = []
        self.html = None
        self.driver = webdriver.Chrome(service=Service(path))
        self.links = []
        self.prices = []
        self.addresses = []

    def get_html_code(self, file):
        file_exists = exists(file)
        if not file_exists:
            self.driver.get(url=RENT_URL)
            self.driver.maximize_window()
            scroll_done = input('scroll done?(Y/N): ').upper()
            if scroll_done == 'Y':
                with open(file, 'w', encoding='UTF-8') as file:
                    html = self.driver.page_source
                    file.write(html)
            self.driver.quit()

    def get_results(self, file):
        with open(file, 'r', encoding='UTF-8') as file:
            zillow_html = file.read()
            soup = BeautifulSoup(zillow_html, 'html.parser')

        self.results = soup.find_all(name="li", class_='ListItem-c11n-8-73-8__sc-10e22w8-0')
        self.links = soup.find_all(name="a", class_='StyledPropertyCardDataArea-c11n-8-73-8__sc-yipmu-0')
        self.links_formatted = [link.get("href") for link in self.links]
        self.links_formatted = [RENT_URL_STATIC + '/b' + str(link).split('/b')[-1] for link in self.links_formatted]
        self.addresses = [link.text.split('|')[-1] for link in self.links]
        self.prices = soup.select(selector=".StyledPropertyCardDataArea-c11n-8-73-8__sc-yipmu-0 span[data-test]")
        self.prices_formatted = [price.text.split('+')[0].split('/mo')[0] for price in self.prices]

    def fill_form(self, path):
        self.driver.get(url=path)
        self.driver.maximize_window()
        sleep(3)
        for num in range(len(self.addresses)):
            question_1 = self.driver.find_element(By.XPATH,
                                                  '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input')
            question_1.send_keys(self.addresses[num])
            sleep(1)
            question_2 = self.driver.find_element(By.XPATH,
                                                  '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input')
            question_2.send_keys(self.prices_formatted[num])
            sleep(1)
            question_3 = self.driver.find_element(By.XPATH,
                                                  '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input')
            question_3.send_keys(self.links_formatted[num])
            sleep(2)
            send_button = self.driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div[1]/div')
            send_button.click()
            sleep(1)
            next_answer = self.driver.find_element(By.LINK_TEXT, 'Prześlij kolejną odpowiedź')
            next_answer.click()
            sleep(1)
            print(num, self.links_formatted[num])
        self.driver.quit()


bot = RentFinder(CHROME_DRIVER_PATH)
bot.get_html_code("code.html")
bot.get_results("code.html")
bot.fill_form(FORM)
