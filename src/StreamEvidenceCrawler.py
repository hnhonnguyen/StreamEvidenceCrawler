
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as soup
from selenium.webdriver.common.action_chains import ActionChains
import utils.utils as utils
from typing import *
from selenium.webdriver.remote.webelement import WebElement


class StreamEvidenceCrawler:
    def __init__(self, url) -> None:
        self.driver: webdriver.Firefox = self.init_driver()
        self.driver.get(url)

    def init_driver(self) -> webdriver.Firefox:
        """This function is to init webdriver

        Returns:
            webdriver: Selenium firefox webdriver
        """
        
        options = FirefoxOptions()
        options.add_argument("--disable-blink-features=AutomationControlled") 
        options.accept_insecure_certs = True
        driver = webdriver.Remote(options=options, command_executor="http://localhost:4444")
        webdriver.Firefox.install_addon(driver, "./extensions/ublock_origin-1.58.0.xpi", temporary=True)

        return driver

    def _get_element(self, by: str, value: str) -> WebElement:
        return WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((by, value)))

    def _get_elements(self, by: str, value: str) -> List[WebElement]:
        return WebDriverWait(self.driver, 60).until(EC.presence_of_all_elements_located((by, value)))
    
    def get_dropdown(self) -> WebElement:
        return self._get_element(By.CLASS_NAME, "btn-seasons")

    def get_seasons(self) -> List[WebElement]:
        return self._get_elements(By.CLASS_NAME, "ss-item")

    def get_episodes(self) -> List[WebElement]:
        utils.sleep()
        return self._get_elements(By.CLASS_NAME, "eps-item")

    def get_movie_name(self) -> str:
        return self._get_element(By.CLASS_NAME, "heading-name").find_element(By.TAG_NAME, "a").text

    def get_current_season_name(self) -> str:
        return self._get_element(By.ID, "current-season").text

    def move_to_element(self, element) -> None:
        utils.sleep()
        action = ActionChains(self.driver)
        action.move_to_element(element).perform()

    def scroll_to_element(self, element) -> None:
        utils.sleep()
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        self.driver.execute_script("window.scrollBy(0, -200);")

    def click_element(self, element):
        utils.sleep()
        self.driver.execute_script("arguments[0].click();", element)
        utils.sleep()

    def get_pagesource(self) -> soup:
        source = self.driver.execute_script('return document.documentElement.outerHTML')
        pagesoup = soup(source, 'html.parser')
        return pagesoup

    def get_url(self) -> str:
        return self.driver.current_url

    def save_screenshot(self, name: str) -> None:
        self.driver.save_screenshot(f"{name}.png")

    def get_binary_screenshot(self) -> bytes:
        return self.driver.get_screenshot_as_png()

    def get_video_play(self) -> WebElement:
        return self._get_element(By.CSS_SELECTOR, ".jw-icon-display")

    def exit(self) -> None:
        self.driver.quit()