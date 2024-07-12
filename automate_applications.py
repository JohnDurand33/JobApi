from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import requests

def solve_captcha(site_key, page_url, api_key):
    url = f"http://2captcha.com/in.php?key={api_key}&method=userrecaptcha&googlekey={site_key}&pageurl={page_url}"
    response = requests.get(url)
    if response.text[0:2] != 'OK':
        return None
    captcha_id = response.text.split('|')[1]
    fetch_url = f"http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}"
    for _ in range(20):
        time.sleep(5)
        result = requests.get(fetch_url)
        if result.text == 'CAPCHA_NOT_READY':
            continue
        if result.text[0:2] == 'OK':
            return result.text.split('|')[1]
    return None

def apply_to_job(job_url, resume_path, api_key):
    driver = webdriver.Chrome()  # Make sure you have chromedriver installed and in PATH
    driver.get(job_url)

    # Example process for filling out an application form
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'first_name'))
        ).send_keys('Your First Name')
        
        driver.find_element(By.NAME, 'last_name').send_keys('Your Last Name')
        driver.find_element(By.NAME, 'email').send_keys('youremail@example.com')
        driver.find_element(By.NAME, 'resume').send_keys(resume_path)

        # Solve CAPTCHA
        site_key = driver.find_element(By.CLASS_NAME, 'g-recaptcha').get_attribute('data-sitekey')
        captcha_solution = solve_captcha(site_key, job_url, api_key)
        driver.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML="{captcha_solution}";')

        # Submit form
        driver.find_element(By.NAME, 'submit').click()
    except Exception as e:
        print(f"Error applying to job: {e}")
    finally:
        driver.quit()

def apply_to_jobs(jobs, resume_path, api_key):
    for job in jobs:
        apply_to_job(job['redirect_url'], resume_path, api_key)
        time.sleep(random.uniform(60, 120))  # Wait between 1 and 2 minutes