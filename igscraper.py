import time
import psycopg2
import config as cfg
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def dbConnect():
    # Establish a connection to database
    try:
        conn = psycopg2.connect(f'host=localhost dbname=sleepingongems user=postgres password={cfg.dbPassword}')
    except psycopg2.Error as e:
        print('ERROR: Connection to sleepingongems unsuccessful.')
        print(e)

    # Initialize cursor to execute queries
    try:
        cur = conn.cursor()
    except psycopg2.Error as e:
        print('ERROR: Cursor initialization unsuccessful.')
        print(e)

    return conn, cur

def createTable(cur):
    # Create table to store collected data
    SQL = 'CREATE TABLE IF NOT EXISTS posts (id SERIAL PRIMARY KEY, \
                                             url VARCHAR(50) NOT NULL, \
                                             date DATE, \
                                             caption TEXT NOT NULL, \
                                             likes INTEGER, \
                                             CONSTRAINT link UNIQUE(url));'
    try:
        cur.execute(SQL)
    except psycopg2.Error as e:
        print('ERROR: Posts table creation unsuccessful.')
        print(e)

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

def balance(caption):
    if "'" in caption or "’" in caption:
        caption = caption.replace("'", "''")
        caption = caption.replace("’", "''")
        
    return caption

def collect(driver, cur):
    # Click initial post
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, 'div[class="_aabd _aa8k  _al3l"]').click()

    # Create SQL query
    SQL = "INSERT INTO posts (url, date, caption, likes) VALUES ('{}', '{}', '{}', '{}');"
    while True:
        time.sleep(2)
        # Collect data
        div = driver.find_element(By.CSS_SELECTOR, 'div[class="x1cy8zhl x9f619 x78zum5 xl56j7k x2lwn1j xeuugli x47corl"]')
        url = driver.current_url.rsplit('/', 1)[:-1][0] +'/'
        try:
            caption = balance(div.find_element(By.XPATH, './/h1').text)
        except NoSuchElementException:
            caption = 'Caption does not exist.'
            pass
        date = div.find_element(By.CSS_SELECTOR, 'time[class="_aaqe"]').get_attribute('datetime').split('T')[0]
        section = div.find_element(By.CSS_SELECTOR, 'section[class="_ae5m _ae5n _ae5o"]')
        likes = int(section.find_element(By.CSS_SELECTOR, '.html-span').text.replace(',',""))
        print('URL: ' + str(url) +
              '\nCaption: ' + caption +
              '\nDate: ' + date +
              '\nLikes: ' + str(likes))
        
        # Check if record exists in database
        try:
            print('CHECK GOES HERE')
            # break
        except psycopg2.Error as e:
            print(e)

        # Insert data record into database
        try:
            cur.execute(SQL.format(url, date, caption, likes))
            print('^ SUCCESS: Inserted ^')
        except psycopg2.Error as e:
            print('^ ERROR: Record insertion unsuccessful. ^')
            print(e)
            pass

        # Click Next arrow, if element does not exist break out of loop (last post reached)
        # Exception should only be reached on first scrape collection
        try:
            driver.find_element(By.CSS_SELECTOR, 'svg[aria-label="Next"]').click()
        except NoSuchElementException:
            print("Reached last post.")
            break

# Connect to SleepingOnGems database & Initialize cursor
conn, cur = dbConnect()
conn.set_session(autocommit=True)

# Create table in database
createTable(cur)

# Initialize Chrome webdriver and go to Instagram
driver = webdriver.Chrome()
driver.get("https://www.instagram.com")

# Login to Instagram
login(driver)

# Search SleepingOnGems profile
search(driver)

# Begin Scraping
collect(driver, cur)

# Close driver, cursor, and connection
driver.quit()
cur.close()
conn.close()
