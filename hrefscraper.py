import time
import psycopg2
import config as cfg
from selenium import webdriver
from selenium.webdriver.common.by import By

def dbConnect():
    try:
        conn = psycopg2.connect(f'host=localhost dbname=sleepingongems user=postgres password={cfg.dbPassword}')
    except psycopg2.Error as e:
        print('ERROR: Connection to sleepingongems unsuccessful.')
        print(e)

    try:
        cur = conn.cursor()
    except psycopg2.Error as e:
        print('ERROR: Cursor initialization unsuccessful.')
        print(e)

    return conn, cur

def login(driver):
    # Enter Username and Password –> Click 'Login'
    time.sleep(2)

    username = driver.find_element(By.CSS_SELECTOR, 'input[name="username"]')
    password = driver.find_element(By.CSS_SELECTOR, 'input[name="password"]')

    username.clear()
    password.clear()

    username.send_keys(cfg.username)
    password.send_keys(cfg.password)

    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    # Handle Save Login Info –> Click 'Not Now'
    time.sleep(5)
    driver.find_element(By.XPATH, '//div[contains(text(), "Not Now")]').click()

    time.sleep(5)
    driver.find_element(By.XPATH, '//button[contains(text(), "Not Now")]').click()

def search(driver):
    time.sleep(2)
    # Click Search Icon
    driver.find_element(By.CSS_SELECTOR, 'svg[aria-label="Search"]').click()
    time.sleep(2)

    # Search sleepingongems in searchbox
    searchbox = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Search"]')
    searchbox.clear()
    searchbox.send_keys('sleepingongems')
    time.sleep(2)

    # Click search result
    driver.find_element(By.CSS_SELECTOR, 'a[href="/sleepingongems/"]').click()
    time.sleep(2)

def collectHrefs(driver, cur):
    # Get beginning scrollHeight
    oldScrollHeight = driver.execute_script('return document.body.scrollHeight;')
    while True:
        print('Old: ' + str(oldScrollHeight))
        # Scroll to load new posts & get posts
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        posts = driver.find_elements(By.CSS_SELECTOR, 'div[class="_aabd _aa8k  _al3l"]')

        time.sleep(2)
        # Obtain href attribute from each post
        for post in posts:
            try:
                href = post.find_element(By.XPATH, './/a').get_attribute('href')
                cur.execute(f"INSERT INTO hrefs (href) VALUES ('{href}') \
                                ON CONFLICT DO NOTHING")
            except psycopg2.Error as e:
                print('ERROR: Record insertion unsuccessful.')
                print(e)
                pass
        
        time.sleep(2)
        newScrollHeight = driver.execute_script('return document.body.scrollHeight;')
        print('New: ' + str(newScrollHeight))
        if newScrollHeight == oldScrollHeight:
            break
        time.sleep(2)
        oldScrollHeight = newScrollHeight

# Connect to SleepingOnGems database & Initialize cursor
conn, cur = dbConnect()
conn.set_session(autocommit=True)

# Initialize Chrome webdriver and go to Instagram
driver = webdriver.Chrome()
driver.get("https://www.instagram.com")

# Login to Instagram
login(driver)

# Search SleepingOnGems profile
search(driver)

# Collect Hrefs
collectHrefs(driver, cur)
