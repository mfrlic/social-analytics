from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common import exceptions
from bs4 import BeautifulSoup as bs
from time import sleep
import re, datetime, json

def start_chromedriver():
    try:
        chrome_options = Options()
        """chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.headless = True"""
        driver = webdriver.Chrome(executable_path='/Users/mario/Documents/chromedriver', options=chrome_options)
        driver.get('https://twitter.com/login')
        return driver
    except:
        print('Failed to start chromedriver. Aborting...')
        exit()
def attempt_login(username, password, driver):
    try:
        WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, '//input[@name="session[username_or_email]"]')))
        username_input = driver.find_element_by_xpath('//input[@name="session[username_or_email]"]')
        username_input.send_keys(username)
    except exceptions.TimeoutException:
        print("Timeout while waiting for login screen. Trying again...")
        attempt_login(username, password, driver)
    password_input = driver.find_element_by_xpath('//input[@name="session[password]"]')
    password_input.send_keys(password)
    try:
        password_input.send_keys(Keys.RETURN)
        url = "https://twitter.com/home"
        WebDriverWait(driver, 3).until(expected_conditions.url_to_be(url))
    except exceptions.TimeoutException:
        print("Timeout while waiting for home screen. Trying again...")
        if 'https://twitter.com/login' in driver.current_url:
            attempt_login(username, password, driver)
        else:
            print('Something has gone wrong. Aborting...')
            exit()
    print('Successful login.')
def find_search_bar(driver, search_term):
    try:
        WebDriverWait(driver, 5).until(expected_conditions.presence_of_element_located((By.XPATH, '//input[@aria-label="Search query"]')))
        search_input = driver.find_element_by_xpath('//input[@aria-label="Search query"]')
        print('Successfully found. Attempting to search...')
        search_input.send_keys(search_term)
        search_input.send_keys(Keys.RETURN)
    except:
        print('Search bar not found. Aborting...')
        exit()
def change_tab(driver, category):
    try:
        WebDriverWait(driver, 5).until(expected_conditions.presence_of_element_located((By.LINK_TEXT, category)))
        driver.find_element_by_link_text(category).click()
        WebDriverWait(driver, 5).until(expected_conditions.presence_of_element_located((By.XPATH, '//div[@data-testid="tweet"]')))
        print('Tab changed. Scrolling...')
    except:
        print('Could not switch tabs. Aborting...')
        exit()
def scroll(driver, last_position, scroll_attempt, loading_time = 0.5, max_attempts = 10):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(loading_time)
    current_position = driver.execute_script("return window.pageYOffset;")
    if current_position == last_position and scroll_attempt > max_attempts:
        driver.execute_script("window.scrollTo(0, 0);")
        scroll(driver, current_position, 0)
    elif current_position == last_position:
        scroll(driver, current_position, scroll_attempt + 1)
    return current_position
def fetch_data(driver, since, until):
    sources, date, last_position = [], until, None
    while date >= since:
        tweets = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
        sources.append(driver.page_source)
        date = datetime.datetime.strptime(tweets[-1].find_element_by_xpath('.//time').get_attribute('datetime').split('T')[0], '%Y-%m-%d').date()
        last_position = scroll(driver, last_position, 0)
    driver.quit()
    return sources
def append_data(sources, data = [], unique_tweets = []):
    for source in sources:
        tweets = bs(source, 'html.parser').find_all('div', {'data-testid': 'tweet'})
        for tweet in tweets:
            handle, date = tweet.find('span', text=re.compile('@')).text, tweet.find('time')['datetime']
            tweet_id = handle + date
            if tweet_id not in unique_tweets:
                unique_tweets.append(tweet_id)
                data.append(date.split('T')[0])
    return data
def sort_data(item):
    return datetime.datetime.strptime(item.get('date'), '%Y-%m-%d').date()
def save_to_json(data, since, until, crypto, dates = [], stats_24h = 0):
    temp = until
    while temp >= since:
        dates.append(str(temp))
        temp -= datetime.timedelta(days=1)

    try:
        with open('data/' + crypto + '.json', 'r') as file:
            json_data = json.load(file)
        stats = json_data.get('twitter_count')
    except:
        stats = []

    for date in dates:
        check = 0
        for item in stats:
            if date == item.get('date'):
                check = 1
                break
        if check == 0:
            stats_24h = 0
            for item in data:
                if item == date:
                    stats_24h+=1
            stats.append({'date': date, 'count': stats_24h})
    stats.sort(key=sort_data)

    json_data['twitter_count'] = stats
    with open('data/' + crypto + '.json', 'w') as file:
        json.dump(json_data, file)
def main(crypto, search_term, since, until, username='myntapp_bot', password='CRV)`q*uuBBnw>gYQ{RUp`!aK./Z)^/^Lv$yJPR37!%;W+z=98F-4{%`$VVNQuG('):
    since = datetime.datetime.strptime(since, '%Y-%m-%d').date()
    until = datetime.datetime.strptime(until, '%Y-%m-%d').date()
    search_term += (' since:' + str(since - datetime.timedelta(days=1)) if since is not None else '') + (' until:' + str(until + datetime.timedelta(days=1) if until is not None else ''))

    print('Starting chromedriver...')
    driver = start_chromedriver()

    print('Attempting to log in...')
    attempt_login(username, password, driver)

    print('Finding search bar...')
    find_search_bar(driver, search_term)

    print('Search successful. Changing the tab to "Latest"...')
    change_tab(driver, 'Latest')

    print('Scrolling and fetching data...')
    sources = fetch_data(driver, since, until)

    print('Scrolling finished. Quitting the chromedriver and appending data to list...')
    data = append_data(sources)

    print('Data appended. Saving data to json...')
    save_to_json(data, since, until, crypto)

    print('Successfully saved to json.')