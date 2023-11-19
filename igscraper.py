import psycopg2
import config as cfg
from db import Database
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

def login(driver):
    # Enter Username and Password –> Click 'Login'
    username = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="username"]')))
    password = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]')))

    username.clear()
    password.clear()

    username.send_keys(cfg.username)
    password.send_keys(cfg.password)

    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]'))).click()

    # Handle Save Login Info –> Click 'Not Now'
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "Not Now")]'))).click()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Not Now")]'))).click()

def search(driver):
    # Click Search Icon
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="Search"]'))).click()

    # Search sleepingongems in searchbox
    searchbox = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Search"]')))
    searchbox.clear()
    searchbox.send_keys('sleepingongems')

    # Click search result
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="/sleepingongems/"]'))).click()

def balance(caption):
    if "'" in caption or "’" in caption:
        caption = caption.replace("'", "''")
        caption = caption.replace("’", "''")
        
    return caption

def collect(driver):
    # Click initial post
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[class="_aabd _aa8k  _al3l"]'))).click()

    while True:
        # Collect data
        div = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="x1cy8zhl x9f619 x78zum5 xl56j7k x2lwn1j xeuugli x47corl"]')))
        url = driver.current_url.rsplit('/', 1)[:-1][0] +'/'
        try:
            caption = balance(div.find_element(By.XPATH, './/h1').text)
        except NoSuchElementException:
            caption = 'Caption does not exist.'
            pass
        date = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'time[class="_aaqe"]'))).get_attribute('datetime').split('T')[0]
        section = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'section[class="_ae5m _ae5n _ae5o"]')))
        likes = int(section.find_element(By.CSS_SELECTOR, '.html-span').text.replace(',',""))
        print('URL: ' + str(url) +
              '\nCaption: ' + caption +
              '\nDate: ' + date +
              '\nLikes: ' + str(likes))
        
        with Database() as db:
            db.set_session(commit=True)

            # Create SQL queries
            insertSQL = "INSERT INTO posts (url, date, caption, likes) VALUES ('{}', '{}', '{}', '{}');"
            checkSQL = "SELECT url FROM posts WHERE url = '{}';"

            # Check if record exists in database
            # If record exists, break (all posts have been added to database)
            try:
                db.execute(checkSQL.format(url))
                if db.fetchone() is not None:
                    print('^ Post exists in database... Ending collection ^')
                    break
            except psycopg2.Error as e:
                print('^ ERROR: Record check unsuccessful. ^')
                print(e)

            # Insert data record into database
            try:
                db.execute(insertSQL.format(url, date, caption, likes))
                print('^ SUCCESS: Inserted ^')
            except psycopg2.Error as e:
                print('^ ERROR: Record insertion unsuccessful. ^')
                print(e)
                pass

        # Click Next arrow, if element does not exist break out of loop (last post reached)
        # Exception should only be reached on first scrape collection
        try:
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="Next"]'))).click()
        except NoSuchElementException:
            print("Reached last post.")
            break

if __name__ == '__main__':
    # Initialize Chrome webdriver and go to Instagram
    driver = webdriver.Chrome()
    driver.get("https://www.instagram.com")

    # Login to Instagram
    login(driver)

    # Search SleepingOnGems profile
    search(driver)

    # Begin Scraping
    collect(driver)

    # Close driver, cursor, and connection
    driver.quit()

