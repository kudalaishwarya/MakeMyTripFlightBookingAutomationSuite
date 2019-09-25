import datetime
import pathlib
import re
import sys
from datetime import date, timedelta
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as cond
from selenium.webdriver.support.ui import WebDriverWait


class MMTAutomationSuite():


    def diff_month(self, d1, d2):
        return (d1.year - d2.year) * 12 + d1.month - d2.month


    def runAutomation(self):

        print('\n***** Welcome to One-Way Flight Booking Automation Suite *****')

        #take valid user inputs
        curr_date, destination, from_date, source, to_date = self.take_valid_user_inputs()

        #initialize driver
        driver, from_place_locator, to_place_locator = self.initialize_chrome_driver()

        #selecting Source and Destination cities in UI
        self.automated_city_selection(destination, driver, from_place_locator, source, to_place_locator)

        #Departure Date-Picker
        self.select_departure_date_window(curr_date, driver, from_date)

        date_format = '%a %b %d %Y'

        #Generate minimum fare details
        min_date, min_price = self.get_minimum_fare_details(date_format, driver, from_date, to_date)

        #Printing Results
        if min_price == 0:
            print('\n\nSorry, No Flights Available')
        else:
            print('\n\nMinimum Pricing of Rs. ' + str(min_price) + ' is available on ' + str(min_date))

        #click final minimum fare date
        self.click_final_flight_date(date_format, driver, min_date, to_date)

        driver.close()

    def click_final_flight_date(self, date_format, driver, min_date, to_date):
        try:
            navigate_final_clicks = self.diff_month(min_date, to_date)
            self.operate_date_navigation(driver, navigate_final_clicks)
            element = driver.find_element_by_xpath('//div[@class="DayPicker-Day" and @aria-label="' + str(
                min_date.strftime(date_format)) + '" and @aria-disabled="false"]')
            element.click()
            driver.implicitly_wait(10)
        except:
            print('Not Found')

    def get_minimum_fare_details(self, date_format, driver, from_date, to_date):
        day = timedelta(days=1)
        min_date = from_date
        min_price = sys.maxsize
        loop_start_date = from_date
        last_processed_date = from_date
        current_price = 0
        while loop_start_date <= to_date:
            # print(from_date.strftime(date_format))
            formatted_date = loop_start_date.strftime(date_format)
            if int(loop_start_date.strftime('%m')) > int(last_processed_date.strftime('%m')):
                date_navigator_next = driver.find_element_by_xpath(Constansts.NAVIGATE_DATE_NEXT)
                date_navigator_next.click()

                element = driver.find_element_by_xpath('(//*[@class="DayPicker-Body"])[1]')
                action = ActionChains(driver)
                action.move_to_element(element).perform()
                driver.implicitly_wait(2)

            try:
                element = driver.find_element_by_xpath('//div[@class="DayPicker-Day" and @aria-label="' + str(
                    formatted_date) + '" and @aria-disabled="false"]//p[2]')
                if element is not None:
                    current_price = int(element.text)
            except:
                pass

            # print(current_price)
            if current_price < min_price:
                min_date = loop_start_date
                min_price = current_price

            last_processed_date = loop_start_date
            loop_start_date = loop_start_date + day
        return min_date, min_price

    def select_departure_date_window(self, curr_date, driver, from_date):
        # Click on departure button
        departure_button = WebDriverWait(driver, 10).until(
            cond.visibility_of_element_located((By.XPATH, Constansts.DEPARTURE_BUTTON)))
        departure_button.click()
        driver.implicitly_wait(2)
        total_months = self.diff_month(from_date, curr_date)
        self.operate_date_navigation(driver, total_months)

    def operate_date_navigation(self, driver, total_months):

        if total_months > 0:
            for months in range(total_months):
                date_navigator_next = driver.find_element_by_xpath(Constansts.NAVIGATE_DATE_NEXT)
                date_navigator_next.click()
        elif total_months < 0:
            for months in range(total_months, 0):
                date_navigator_prev = driver.find_element_by_xpath(Constansts.NAVIGATE_DATE_PREV)
                date_navigator_prev.click()

        element = driver.find_element_by_xpath(Constansts.DATE_PICKER_BODY)
        action = ActionChains(driver)
        action.move_to_element(element).perform()
        driver.implicitly_wait(2)

    def automated_city_selection(self, destination, driver, from_place_locator, source, to_place_locator):
        # Selecting Source city
        from_place_locator.click()
        driver.implicitly_wait(4)
        from_place_search = WebDriverWait(driver, 10).until(
            cond.visibility_of_element_located((By.XPATH, Constansts.SEARCH_BOX_FROM_CITY)))
        from_place_search.click()
        driver.implicitly_wait(4)
        from_place_search.send_keys(source)
        WebDriverWait(driver, 20).until(
            cond.visibility_of_all_elements_located((By.XPATH, Constansts.SEARCH_BOX_RESULTS)))
        source_city_list = driver.find_elements(By.XPATH, Constansts.SEARCH_BOX_RESULTS)
        is_clicked = 0
        attempts = 0
        while attempts < 2:
            try:
                for web in source_city_list:
                    driver.implicitly_wait(4)
                    webText = web.text
                    if re.search(source, webText, re.IGNORECASE):
                        driver.implicitly_wait(4)
                        web.click()
                        driver.implicitly_wait(2)
                        is_clicked = 1
                        break
            except:
                pass
            attempts += 1

        # inputCity = driver.find_element(By.ID,'fromCity').text
        if is_clicked == 0:
            print('\n\n' + source + ' city is currently not available in listing')
            driver.close()
            exit()
        # Selecting Destination City
        driver.implicitly_wait(4)
        to_place_locator.click()
        driver.implicitly_wait(2)
        to_place_search = WebDriverWait(driver, 10).until(
            cond.visibility_of_element_located((By.XPATH, Constansts.SEARCH_BOX_TO_CITY)))
        to_place_search.click()
        driver.implicitly_wait(4)
        to_place_search.send_keys(destination)
        WebDriverWait(driver, 20).until(
            cond.visibility_of_all_elements_located((By.XPATH, Constansts.SEARCH_BOX_RESULTS)))
        destinationCityList = driver.find_elements(By.XPATH, Constansts.SEARCH_BOX_RESULTS)
        attempts = 0
        while attempts < 2:
            try:
                for web in destinationCityList:
                    webText = web.text
                    if re.search(destination, webText, re.IGNORECASE):
                        driver.implicitly_wait(3)
                        web.click()
                        is_clicked = 2
                        driver.implicitly_wait(5)
                        break
            except:
                pass
            attempts += 1

        if is_clicked != 2:
            print('\n\n' + destination + ' city is currently not available in listing')
            driver.close()
            exit()

    def initialize_chrome_driver(self):
        fn = pathlib.Path(__file__).parent / '../resources/chromedriver'
        driver = webdriver.Chrome(fn)
        # driver = self.driver
        driver.implicitly_wait(2)
        driver.get(Constansts.WEB_URL)
        driver.implicitly_wait(5)
        driver.maximize_window()
        wait = WebDriverWait(driver, 10)
        # print(source)
        # print(destination)
        oneway = driver.find_element_by_xpath(Constansts.ONE_WAY_CHECKBOX)
        from_place_locator = driver.find_element_by_xpath(Constansts.FROM_CITY_LOCATOR)
        to_place_locator = driver.find_element_by_xpath(Constansts.TO_CITY_LOCATOR)
        return driver, from_place_locator, to_place_locator


    def take_valid_user_inputs(self):

        source = input('\n\nPlease enter Source City - ')
        destination = input('Please enter Destination City - ')
        print('\n\nPlease Enter Departure date range')
        # Input Start Date
        departure_from_date = input('\nPlease enter Start Date (Format : DD-MM-YYYY ) : ')
        curr_date = date.today()
        try:
            day1, month1, year1 = map(int, departure_from_date.split('-'))
            from_date = datetime.date(year1, month1, day1)
        except:
            print('Invalid Date Entered')
            exit()
        while from_date < curr_date:
            print('Please enter date as today or future')
            departure_from_date = input('Please enter Start Date (Format : DD-MM-YYYY ) : ')
        # Input End Date
        departure_end_date = input('Please enter End Date (Format : DD-MM-YYYY ) : ')

        try:
            day2, month2, year2 = map(int, departure_end_date.split('-'))
            to_date = datetime.date(year2, month2, day2)
        except:
            print('Invalid Date Entered')
            exit()

        while to_date < from_date:
            print('Please enter a future date')
            departure_end_date = input('Please enter End Date (Format : DD-MM-YYYY ) : ')
            day2, month2, year2 = map(int, departure_end_date.split('-'))
            to_date = datetime.date(year2, month2, day2)

        return curr_date, destination, from_date, source, to_date

class Constansts:
    NAVIGATE_DATE_NEXT = '//div[@class="DayPicker-NavBar"]//span[@class="DayPicker-NavButton DayPicker-NavButton--next"]'
    NAVIGATE_DATE_PREV = '//div[@class="DayPicker-NavBar"]//span[@class="DayPicker-NavButton DayPicker-NavButton--prev"]'
    DEPARTURE_BUTTON = '//span[contains(text(),"DEPARTURE")]'
    DATE_PICKER_BODY = '(//*[@class="DayPicker-Body"])[1]'
    SEARCH_BOX_FROM_CITY = '//input[contains(@placeholder,"From")]'
    SEARCH_BOX_TO_CITY = '//input[@placeholder="To"]'
    #SEARCH_BOX_RESULTS = '//p[@class="font14 appendBottom5 blackText"]'
    SEARCH_BOX_RESULTS = '//div[@class="hsw_autocomplePopup autoSuggestPlugin"]//div[@class="makeFlex hrtlCenter"]//div[@class="calc60"]//p[@class="font14 appendBottom5 blackText"]'
    WEB_URL = 'https://www.makemytrip.com'
    ONE_WAY_CHECKBOX = '//li[@class="selected"]'
    FROM_CITY_LOCATOR = '//span[contains(@class,"appendBottom5")][contains(text(),"From")]'
    TO_CITY_LOCATOR = '//span[contains(@class,"appendBottom5")][contains(text(),"To")]'


if __name__ == '__main__':

    suite = MMTAutomationSuite()
    suite.runAutomation()
