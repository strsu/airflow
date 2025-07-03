import os
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent

class SeleniumManager:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--disable-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument(f"user-agent={UserAgent('mobile').random}")

        self.driver = None
        self.chrome_options = chrome_options
        self.service = Service("/usr/local/bin/chromedriver")
        self.load_driver()

    def load_driver(self):
        try:
            self.driver = webdriver.Chrome(
                service=self.service, options=self.chrome_options
            )
        except Exception as e:
            print(f"Chrome 드라이버 로드 실패: {e}")
            # Chrome 버전 확인
            try:
                result = subprocess.run(['google-chrome', '--version'], 
                                      capture_output=True, text=True)
                print(f"시스템 Chrome 버전: {result.stdout.strip()}")
            except:
                print("Chrome 버전 확인 실패")
            raise e

    def get_driver(self):
        if not self.driver:
            self.load_driver()
        return self.driver
    
    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None