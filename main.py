import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

# Config URL
# it's better to use a URL where review page has opened the ‘More Reviews’ button
URL = "https://www.google.com/maps/place/Taman+Istana+Osaka/@34.685917,135.519312,15.54z/data=!4m18!1m9!3m8!1s0x6000e0cd5c283afd:0xf01d07d5ca11e41!2sIstana+Osaka!8m2!3d34.6872571!4d135.5258546!9m1!1b1!16zL20vMDI0Yl9n!3m7!1s0x6000e0c977655555:0x67f69eaef984d98b!8m2!3d34.6864797!4d135.5262114!9m1!1b1!16s%2Fm%2F05s_qsc?entry=ttu&g_ep=EgoyMDI1MTEwNC4xIKXMDSoASAFQAw%3D%3D"
JUMLAH_SCROLL = 10

print(f"Start scraping from: {URL}")

# Setup library
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

driver.get(URL)

print("[INFO] Loading page...")
time.sleep(5)

# Finding Reviews panel
print("[INFO] Find Review Panel...")
try:
    scrollable_panel = driver.find_element(By.XPATH, "//div[@role='main']")
    print("[SUCCESS] Panel (@role='main') Found!!.")
    
except NoSuchElementException:
    print("[FAILED] Can't find Review Panel (@role='main'). Try Again.")
    driver.quit()
    exit() 

# Scrolling
print(f"[INFO] Start Scraping: {JUMLAH_SCROLL}x scroll...")
for i in range(JUMLAH_SCROLL):
    try:
        # Finding class 'jftiEf'
        review_elements_in_loop = driver.find_elements(By.CLASS_NAME, 'jftiEf')
        
        if not review_elements_in_loop:
            print("[INFO] Can't Find 'jftiEf' Element.")
            break

        last_review = review_elements_in_loop[-1]
        driver.execute_script("arguments[0].scrollIntoView(true);", last_review)
        time.sleep(4) 
        
        # Re'check class 'jftiEf'
        new_review_count = len(driver.find_elements(By.CLASS_NAME, 'jftiEf'))
        
        if new_review_count == len(review_elements_in_loop):
            print("[INFO] No more reviews found.")
            break 
        else:
            # Report
            print(f"[INFO] Scroll-{i+1}: Success. Reviews Total: {new_review_count}")

    except Exception as e:
        print(f"[ERROR] {e}")
        break

# Extract element
print("[INFO] Scroll Finished. Start Extracting...")
review_elements = driver.find_elements(By.CLASS_NAME, 'jftiEf') 

if not review_elements:
    print("[INFO] 'jftiEf' is Empty.")
else:
    print(f"[SUCCESS] Found {len(review_elements)} reviews. Start extracting data...")
    
    review_result = []
    for element in review_elements:
        try:
            # Extact Name
            reviewer_name = element.find_element(By.CLASS_NAME, 'd4r55').text
            # Extract rating
            rating = element.find_element(By.CLASS_NAME, 'kvMYJc').get_attribute('aria-label')
            # Time
            review_time = element.find_element(By.CLASS_NAME, 'rsqaWe').text
            # Click button for more reviews
            try:
                more_button = element.find_element(By.CLASS_NAME, 'w8nwRe')
                more_button.click()
                time.sleep(0.5)
            except NoSuchElementException:
                pass 
            # Extract Text
            review_text = element.find_element(By.CLASS_NAME, 'wiI7pd').text
            # Append data
            review_result.append({
                'review_name': reviewer_name,
                'review_time': review_time,
                'rating': rating,
                'review_text': review_text
            })
        except Exception:
            continue
    # Save as CSV
    if review_result:
        df = pd.DataFrame(review_result)
        filePath = 'Osaka-Castle-2' # CSV File name
        df.to_csv(f"{filePath}.csv", index=False)
        print(f"[INFO] Success! {len(df)} reviews has been save to {filePath}")
    else:
        print("[ERROR] Failed to extact data")

# Close Browser
driver.quit()