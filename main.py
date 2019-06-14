import pandas as pd
from pandas import ExcelWriter
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
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


chromeOptions = Options()
chromeOptions.add_argument("--kiosk")
chromeOptions.add_argument("--headless")

driver = webdriver.Chrome(options=chromeOptions)
secondDriver = webdriver.Chrome(options=chromeOptions)

url = 'https://maps.google.com'
driver.get(url)

# inputs
searchTerm = 'Things to do in Prague, Czech Republic'
cityName = 'Prague, Czech Republic'
baseURL = 'https://www.google.com/maps/search/'
plusURL = searchTerm.replace(' ', '+')
mainURL = baseURL + plusURL
df = pd.DataFrame()

# search for things

element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, 'searchboxinput')))
searchInput = driver.find_element_by_id('searchboxinput')
searchInput.send_keys(searchTerm)
searchInput.send_keys(Keys.RETURN)

# wait for some time
element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CLASS_NAME, 'section-result-title')))

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

# Additional listName of each Activity
pageURLList = []
editorialQuoteList = []
addressList = []
daysAndTimingsList = []
websiteInfoList = []
phoneNumberList = []
coverImageList = []
firstThreeReviewsList = []
opensAtList = []
latitudeList = []
longitudeList = []

counter = len(activityName)

for elem in range(counter):
    activityName[elem].click()
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "section-editorial-quote")))

    pageURL = driver.current_url
    pageURLList.append(pageURL)

    coordinateHolder = str(pageURL).split('/')
    coordinateTemp = ''
    coordinateAvailable = True
    for elem in coordinateHolder:
        if '@' in elem:
            coordinateTemp = elem
            break

    coordinateString = coordinateTemp.strip('@z')
    coordinateList = coordinateString.split(',')
    if coordinateAvailable:
        latitudeList.append(coordinateList[0])
        longitudeList.append(coordinateList[1])
    else:
        latitudeList.append('unavailable')
        longitudeList.append('unavailable')

    try:
        editorialQuote = driver.find_element_by_class_name('section-editorial-quote')
        editorialQuoteList.append(editorialQuote.find_element_by_tag_name('span').get_attribute('innerHTML'))
    except NoSuchElementException:
        editorialQuoteList.append('NA')

    try:
        address = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[10]/div/div[1]/span[3]/span[3]')
        if cityName in address.get_attribute('innerHTML'):
            addressList.append(address.get_attribute('innerHTML'))
        else:
            addressList.append(cityName)
    except NoSuchElementException:
        addressList.append('NA')

    try:
        daysAndTimingsWrap = driver.find_element_by_class_name('section-popular-times')
        daysAndTimings = daysAndTimingsWrap.find_element_by_class_name('goog-menu-button-caption')
        daysAndTimingsList.append(daysAndTimings.get_attribute('innerHTML'))
    except NoSuchElementException:
        daysAndTimingsList.append('NA')

    try:
        websiteInfo = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[12]/div/div[1]/span[3]/span[3]')
        websiteInfoList.append(websiteInfo.get_attribute('innerHTML'))
    except NoSuchElementException:
        websiteInfoList.append('NA')

    try:
        phoneNumber = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[13]/div/div[1]/span[3]/span[3]')
        phoneNumberList.append(phoneNumber.get_attribute('innerHTML'))
    except NoSuchElementException:
        phoneNumberList.append('NA')

    try:
        coverImageWrap = driver.find_element_by_class_name('section-hero-header-hero')
        coverImage = driver.find_element_by_tag_name('img')
        coverImageList.append(coverImage.get_attribute('src'))
    except NoSuchElementException:
        coverImageList.append('NA')

    try:
        opensAt = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[14]/div[1]/span[2]/span[2]')
        opensAtList.append(opensAt.get_attribute('innerHTML'))
    except NoSuchElementException:
        opensAtList.append('NA')

    # to go back to the main page
    driver.get(mainURL)
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'section-result-title')))
    activityName = driver.find_elements_by_class_name('section-result-title')

    # Adding listName in Dataframe
    basicInfo = list(zip(activityNameList, descriptionList, activityRatingList, reviewsList, locationTypeList,
                         pageURLList, editorialQuoteList, addressList, daysAndTimingsList, websiteInfoList, phoneNumberList,
                         coverImageList, opensAtList, latitudeList, longitudeList))
    df = pd.DataFrame(basicInfo, columns=['Name of Activity', 'Description', 'Ratings', 'Number of Reviews', 'Location Type'
                                          , 'Page URL', 'Editorial Quote', 'Address', 'Days and Timings', 'Website Info',
                                          'Phone number', 'Cover Image', 'Opens At', 'Latitude', 'Longitude'])

driver.quit()

with ExcelWriter('record.xlsx') as writer:
    df.to_excel(writer)
