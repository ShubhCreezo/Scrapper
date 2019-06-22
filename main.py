# all imports
import pandas as pd
import time
from pandas import ExcelWriter
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException, TimeoutException, ElementClickInterceptedException,
                                        StaleElementReferenceException)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# function to make Lists from page source
def makeList(listSource, listName):
    listName.clear()
    for elem in listSource:
        listNameWrap = elem.find_element_by_tag_name("span")
        listName.append(listNameWrap.get_attribute("innerHTML"))


def makeList1(listSource, listName):
    listName.clear()
    for elem in listSource:
        listName.append(elem.get_attribute('innerHTML'))


# settings for selenium driver
chromeOptions = Options()
chromeOptions.add_argument("--kiosk")
# comment below line for running script without GUI
# chromeOptions.add_argument("--headless")

# launching automated session
driver = webdriver.Chrome(options=chromeOptions)
url = 'https://maps.google.com'

# let's call google maps
counter = 0


def mainSite(counter, url):
    try:
        driver.get(url)
    except TimeoutException:
        counter += 1
        if counter < 5:
            mainSite(counter, url)
    except:
        print('Try again after some time!!!')


mainSite(counter, url)

# input the city we want to search
cityName = 'Lucerne, Switzerland'
searchTerm = 'Things to do in ' + cityName

# search for activities in the city

element = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.ID, 'searchboxinput')))
searchInput = driver.find_element_by_id('searchboxinput')
searchInput.send_keys(searchTerm)
searchInput.send_keys(Keys.RETURN)
print('search completed')


def main(maindf2, cityName2, dfReturn2):

    # wait for results
    element = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'section-result-title')))

    while True:
        try:
            # Basic listName of Activities in a city
            activityNameList = []
            activityName = driver.find_elements_by_class_name('section-result-title')
            descriptionList = []
            description = driver.find_elements_by_class_name('section-result-description')
            activityRatingList = []
            activityRating = driver.find_elements_by_class_name('section-result-rating')
            reviewsList = []
            reviews = driver.find_elements_by_class_name('section-result-num-ratings')
            locationTypeList = []
            locationType = driver.find_elements_by_class_name('section-result-details')

            makeList(activityName, activityNameList)
            makeList(description, descriptionList)
            makeList(activityRating, activityRatingList)
            makeList1(reviews, reviewsList)
            makeList1(locationType, locationTypeList)
        except StaleElementReferenceException:
            continue  # If StaleElement appears, try again
        break  # once try is successful, stop while loop

    # Additional listName of each Activity
    pageURLList = []
    editorialQuoteList = []
    addressList = []
    daysAndTimingsList = []
    websiteInfoList = []
    phoneNumberList = []
    coverImageList = []
    opensAtList = []
    latitudeList = []
    longitudeList = []

    counter = len(activityName)

    for elem in range(counter-1):
        pageFound = True
        # this clicks at one activity according to index
        try:
            activityName[elem].click()
        except ElementClickInterceptedException:
            time.sleep(2)
            activityName[elem].click()
        except:
            time.sleep(2)
            activityName = driver.find_elements_by_class_name('section-result-title')
            activityName[elem].click()

        print('elem ', elem)

        # if any activity is taking too long to load then we skip it
        def checkPlace(pageFound):
            try:
                element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "section-editorial-quote")))
                pageFound = True
            except TimeoutException:
                print('skipped one place!!!')
                pageFound = False
            return pageFound
        checkPlace(pageFound)

        # now we parse all the details of any particular activity
        if pageFound:
            # this gets page url
            pageURL = driver.current_url
            pageURLList.append(pageURL)

            # this gets latitudes and longitudes
            coordinateHolder = str(pageURL).split('/')
            coordinateTemp = ''
            coordinateAvailable = True
            for elem1 in coordinateHolder:
                if '@' in elem1:
                    coordinateTemp = elem1
                    coordinateAvailable = True
                    break
                else:
                    coordinateAvailable = False

            coordinateString = coordinateTemp.strip('@z')
            coordinateList = coordinateString.split(',')
            if coordinateAvailable:
                latitudeList.append(coordinateList[0])
                longitudeList.append(coordinateList[1])
            else:
                latitudeList.append('unavailable')
                longitudeList.append('unavailable')

            # this gets editorial quote
            try:
                editorialQuote = driver.find_element_by_class_name('section-editorial-quote')
                editorialQuoteList.append(editorialQuote.find_element_by_tag_name('span').get_attribute('innerHTML'))
            except NoSuchElementException:
                editorialQuoteList.append('NA')

            # this gets address of the activity
            try:
                address = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[10]/div/div[1]/span[3]/span[3]')
                if cityName2 in address.get_attribute('innerHTML'):
                    addressList.append(address.get_attribute('innerHTML'))
                else:
                    addressList.append(cityName2)
            except NoSuchElementException:
                addressList.append('NA')

            # this gets Date and Timing info
            try:
                daysAndTimingsWrap = driver.find_element_by_class_name('section-popular-times')
                daysAndTimings = daysAndTimingsWrap.find_element_by_class_name('goog-menu-button-caption')
                daysAndTimingsList.append(daysAndTimings.get_attribute('innerHTML'))
            except NoSuchElementException:
                daysAndTimingsList.append('NA')

            # this gets web info of activity
            try:
                websiteInfo = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[12]/div/div[1]/span[3]/span[3]')
                websiteInfoList.append(websiteInfo.get_attribute('innerHTML'))
            except NoSuchElementException:
                websiteInfoList.append('NA')

            # this gets the phone number
            try:
                phoneNumber = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[13]/div/div[1]/span[3]/span[3]')
                phoneNumberList.append(phoneNumber.get_attribute('innerHTML'))
            except NoSuchElementException:
                phoneNumberList.append('NA')

            # this gets the cover Image
            try:
                coverImageWrap = driver.find_element_by_class_name('section-hero-header-image-hero')
                coverImage = coverImageWrap.find_element_by_tag_name('img')
                coverImageList.append(coverImage.get_attribute('src'))
            except NoSuchElementException:
                coverImageList.append('NA')

            # this gets the time at which activity starts
            try:
                opensAtWrap = driver.find_element_by_class_name('section-info-hour-text')
                # opensAt = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[14]/div[1]/span[2]/span[2]')
                opensAt = opensAtWrap.find_elements_by_tag_name('span')
                opensAtList.append(opensAt[1].get_attribute('innerHTML'))
            except NoSuchElementException:
                opensAtList.append('NA')

        # to go back to the main page
        print('calling main URL...')
        while True:
            try:
                driver.find_element_by_class_name('section-back-to-list-button').click()
            except NoSuchElementException:
                continue
            break
        # we wait to go back to all activities page
        try:
            element = WebDriverWait(driver, 200).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'section-result-title')))
        except TimeoutException:
            time.sleep(2)
            print('May have to try again!!!')
        # we again prepare a list because the page is dynamic
        activityName = driver.find_elements_by_class_name('section-result-title')

    # Adding listName in Dataframe
    basicInfo = list(zip(activityNameList, descriptionList, activityRatingList, reviewsList, locationTypeList,
                         pageURLList, editorialQuoteList, addressList, daysAndTimingsList, websiteInfoList,
                         phoneNumberList, coverImageList, opensAtList, latitudeList, longitudeList))
    df = pd.DataFrame(basicInfo, columns=['Name of Activity', 'Description', 'Ratings', 'Number of Reviews',
                                          'Location Type', 'Page URL', 'Editorial Quote', 'Address', 'Days and Timings',
                                          'Website Info', 'Phone number', 'Cover Image', 'Opens At', 'Latitude',
                                          'Longitude'])
    dfReturn2 = maindf2.append(df, ignore_index=True)
    return dfReturn2


maindf = pd.DataFrame(columns=['Name of Activity', 'Description', 'Ratings', 'Number of Reviews',
                               'Location Type', 'Page URL', 'Editorial Quote', 'Address', 'Days and Timings',
                               'Website Info', 'Phone number', 'Cover Image', 'Opens At', 'Latitude', 'Longitude'])
dfReturn = pd.DataFrame()
pageCounter = 0


def nextPageActivities(maindf1, cityName1, dfReturn1):
    dfReturn1 = main(maindf1, cityName1, dfReturn1)
    maindf1 = dfReturn1
    while True:
        try:
            nextPage = driver.find_element_by_xpath('//*[@id="n7lv7yjyC35__section-pagination-button-next"]')
            if nextPage.is_enabled():
                print('page found')
                time.sleep(2)
                nextPage.click()
                nextPageActivities(maindf1, cityName1, dfReturn1)
            else:
                print('recording in excel')
                with ExcelWriter('record.xlsx') as writer:
                    dfReturn1.to_excel(writer)
        except NoSuchElementException:
            print('We are done here!!! lol')
        except ElementClickInterceptedException:
            if nextPage.is_enabled():
                print('page found')
                time.sleep(2)
                nextPage.click()
                nextPageActivities(maindf1, cityName1, dfReturn1)
        except StaleElementReferenceException:
            continue
        break


nextPageActivities(maindf, cityName, dfReturn)
driver.quit()



