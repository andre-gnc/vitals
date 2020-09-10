import os
import time

import pandas
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def make_driver_chrome(mdc_url):
    mdc_driver = webdriver.Chrome(executable_path=os.path.abspath('chromedriver.exe'))
    mdc_driver.get(mdc_url)
    return mdc_driver


TIMEOUT = 60

item_no = 0
excel_entries = 0
item_dict = {}
page = 0
test_page_amount = 5
doctor_amount = 50
page_test = 'no'
street = ''
city = ''
state = ''
telephone = ''
postal_code = ''

# url = 'https://www.vitals.com/search?ola=false&sid=29236&overall_range=any&virtualVisit=false&query=Cardiology&latLng' \
#       '=33.5723,-112.089&city_state=Phoenix,%20AZ '

url = 'https://www.vitals.com/search?ola=false&sid=29236&overall_range=any&virtualVisit=false&query=&latLng=33.5723,' \
      '-112.089&city_state=Phoenix,%20AZ&count=21&start=0 '

main_driver = make_driver_chrome(url)

wait = WebDriverWait(main_driver, TIMEOUT)
wait_tag = wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'search-results-container')))
time.sleep(3)

while True:

    page += 1

    # print('Page: ' + str(page))
    # print('Page url: ' + url)
    # print('\n')

    # main_driver = make_driver_chrome(url)
    #
    # wait = WebDriverWait(main_driver, TIMEOUT)
    # wait_tag = wait.until(
    #     expected_conditions.presence_of_element_located((By.CLASS_NAME, 'search-results-container')))
    # time.sleep(3)

    # doctors = wait_tag.find_elements_by_class_name('provider-card')
    doctors = main_driver.find_elements_by_class_name('provider-card')
    # ==============================================================================================
    # print('Doctors Amount: ' + str(len(doctors) - 3))
    # print('\n')
    for doctors_counter, doctor in enumerate(doctors, 1):
        try:
            name = doctor.find_element_by_class_name('card-title').find_element_by_class_name('name').text
            values = item_dict.values()
            if name in [x for v in values for x in v if type(v) == list] or name in values:
                continue
        except (NoSuchElementException, StaleElementReferenceException):
            name = ''

        try:
            doctor_url = doctor.find_element_by_class_name('card-title').get_attribute('href')
        except StaleElementReferenceException:
            doctor_url = 'Grab it manually please!'
            name = 'Grab it manually please!'
            street = 'Grab it manually please!'
            city = 'Grab it manually please!'
            state = 'Grab it manually please!'
            postal_code = 'Grab it manually please!'
            telephone = 'Grab it manually please!'
            excel_entries += 1
            item_no += 1
            item_dict[item_no] = [doctor_url, name, street, city, state, postal_code, telephone]
            continue

        if doctors_counter <= 3 or doctors_counter >= doctor_amount:
            continue

        # if page != 1 and (doctors_counter <= 3 + 9 or doctors_counter >= doctor_amount):
        #     continue
        # elif doctors_counter <= 3 or doctors_counter >= doctor_amount:
        #     continue

        # ==========================================================================================
        # print(doctor_url)

        doctor_driver = make_driver_chrome(doctor_url)
        doctor_wait = WebDriverWait(doctor_driver, TIMEOUT)
        button = doctor_wait.until(expected_conditions.element_to_be_clickable((
            By.XPATH, '/html/body/div[1]/div[6]/div[2]/div/div[1]/div/div/div/a[3]')))
        # time.sleep(1)
        button.click()
        time.sleep(1)

        # try:
        #     name_w_score = doctor_driver.find_element_by_class_name(
        #         'name.valign-wrapper').find_element_by_tag_name('h1').text
        #     score_position = name_w_score.rfind('-')
        #     name = name_w_score[:score_position - 1]
        # except NoSuchElementException:
        #     name = 'Grab name manually please!'

        try:
            locations = doctor_driver.find_elements_by_class_name('location-line')
            for locations_counter, location in enumerate(locations, 1):
                try:
                    telephone = location.find_element_by_class_name('phone').text
                    addresses = location.find_elements_by_tag_name('span')
                    for addresses_counter, address in enumerate(addresses, 1):
                        if addresses_counter == 1 \
                                or addresses_counter == 2:
                            continue
                        elif addresses_counter == 3:
                            street = address.text
                        elif addresses_counter == 4:
                            city_w_coma = address.text
                            city_w_coma_position = city_w_coma.find(',')
                            city = city_w_coma[:city_w_coma_position]
                        elif addresses_counter == 5:
                            state = address.text
                        elif addresses_counter == 6:
                            postal_code = address.text
                        else:
                            break
                    break
                except NoSuchElementException:
                    telephone = 'Grab telephone manually please!'
        except NoSuchElementException:
            locations = ''

        excel_entries += 1
        item_no += 1
        item_dict[item_no] = [doctor_url, name, street, city, state, postal_code, telephone]

        if excel_entries == 10:
            df_items = pandas.DataFrame.from_dict(
                item_dict, orient='Index',
                columns=['Url', 'Name', 'Street', 'City', 'State', 'Postal Code', 'Telephone'])
            df_items.to_excel('data.xlsx')
            # df_items.to_csv('data.csv')
            excel_entries = 0

        print(item_no)
        print('Url: ' + doctor_url)
        print('Name: ' + name)
        # print('Locations Amount: ' + str(len(locations)))
        print('Street: ' + street)
        print('City: ' + city)
        print('State: ' + state)
        print('Postal Code: ' + postal_code)
        print('Telephone: ' + telephone)
        print(item_no)
        print('\n')

        doctor_driver.quit()

    try:
        next_button = main_driver.find_element_by_class_name('btn-next')
        next_button.click()
        next_url = main_driver.current_url
        # url = main_driver.find_element_by_css_selector('a.paginator_item.next.item').get_attribute('href')
        time.sleep(10)
    except NoSuchElementException:
        print('Last page. It\'s finished')
        main_driver.quit()
        break

    # url_equal_position = url.rfind('=')
    # url = url[:url_equal_position] + str(page * 21)

    # main_driver.quit()

    if page == test_page_amount and page_test == 'yes':
        main_driver.quit()
        # print('Next url: ' + next_url)
        break

df_items = pandas.DataFrame.from_dict(
    item_dict, orient='Index', columns=['Url', 'Name', 'Street', 'City', 'State', 'Postal Code', 'Telephone'])
df_items.to_excel('data.xlsx')
# df_items.to_csv('data.csv')
