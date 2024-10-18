import os
import pickle
import time
import sys
import difflib
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# X platformuna giriş yapacak bilgiler
USERNAME = 'username'  # X kullanıcı adı
PASSWORD = 'password'  # X şifresi

# Cookie dosyası
COOKIE_FILE = "x_cookies.pkl"

def login(driver):
    driver.get("https://x.com/i/flow/login")
    time.sleep(2)
    
    # Kullanıcı adı ve şifre girişi
    username_field = driver.find_element(By.NAME, "text")
    username_field.send_keys(USERNAME)
    username_field.send_keys(Keys.RETURN)
    
    time.sleep(2)
    
    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys(PASSWORD)
    password_field.send_keys(Keys.RETURN)
    
    time.sleep(3)

    # Giriş başarılıysa cookie'leri kaydet
    cookies = driver.get_cookies()
    with open(COOKIE_FILE, "wb") as file:
        pickle.dump(cookies, file)

def load_cookies(driver):
    # Eğer cookie dosyası varsa cookie'leri yükle
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
        return True
    return False

def search_tweet(driver, tweet_part):
    driver.get("https://twitter.com/search")
    time.sleep(2)
    
    # Arama kutusuna hedef tweetin bir bölümünü yaz
    search_box = driver.find_element(By.XPATH, "//input[@data-testid='SearchBox_Search_Input']")
    search_box.send_keys(tweet_part)
    search_box.send_keys(Keys.RETURN)
    
    time.sleep(3)

    last_tweets_button = driver.find_element(By.XPATH, "//span[text()='En Son']")
    last_tweets_button.click()

    time.sleep(3)

def is_similar(tweet_text, tweet_part, threshold):
    similarity = difflib.SequenceMatcher(None, tweet_text, tweet_part).ratio()
    print(f"Eşleşme oranı: {similarity}")
    return similarity >= threshold

def find_and_block_tweet_users(driver, tweet_part, threshold):
    # Arama sonuçlarında tweetleri bul
    tweets = driver.find_elements(By.XPATH, "//article[@data-testid='tweet']")
    for tweet in tweets:
        # Tweetin tam eşleşmesini kontrol et
        tweet_text = tweet.text
        if is_similar(tweet_text, tweet_part, threshold):
            caret = tweet.find_element(By.XPATH, "//button[@data-testid='caret']")
            caret.click()
            time.sleep(3)

            block = tweet.find_element(By.XPATH, "//div[@data-testid='block']")
            block.click()
            time.sleep(3)
            
            confirm_button = driver.find_element(By.XPATH, "//button[@data-testid='confirmationSheetConfirm']")
            confirm_button.click()
            time.sleep(3)
        else:
            print(f"Tweet eşleşmedi: {tweet_text}")
            continue

def main(tweet_part, threshold):
    # WebDriver ayarları
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    
    try:
        driver.get("https://x.com")
        time.sleep(2)
        
        # Cookie'leri yüklemeye çalış
        if not load_cookies(driver):
            print("No cookies found. Logging in.")
            login(driver)
        else:
            driver.refresh()
            time.sleep(3)
            print("Loaded cookies successfully.")
        
        search_tweet(driver, tweet_part)
        find_and_block_tweet_users(driver, tweet_part, threshold)
    
    finally:
        driver.quit()

if __name__ == "__main__":
    # Argümanları ayarlamak için argparse kullanımı
    parser = argparse.ArgumentParser(description='Tweet arama ve kullanıcıları engelleme programı.')
    parser.add_argument('--query', type=str, required=True, help='Hedef tweetin bir bölümü.')
    parser.add_argument('-T', '--threshold', type=float, default=0.4, help='Eşleşme oranı için minimum değer (0 ile 1 arasında). Varsayılan: 0.4')
    
    args = parser.parse_args()
    
    tweet_part = args.query
    threshold = args.threshold
    
    main(tweet_part, threshold)
