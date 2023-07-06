# import libraries
import os
import platform
import smtplib
import ssl
import pandas as pd
import arbitrage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from scrapers import ladbrokes, tonybet, unibet
from email.message import EmailMessage
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()
email1 = os.getenv("EMAIL1")
email2 = os.getenv("EMAIL2")
password = os.getenv("EMAIL_PASSWORD")

def main():
    if platform.system() == "Windows":
        # headless options set-up
        #options = ChromeOptions()
        #options.add_argument("--headless=new")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install())) #, options=options
    else:
        # headless options set-up for linux
        options = ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("window-size=1400,2100") 
        options.add_argument('--disable-gpu')
        
        # chrome_prefs = {}
        # options.experimental_options["prefs"] = chrome_prefs
        # chrome_prefs["profile.default_content_settings"] = {"images": 2}
        
        driver = webdriver.Chrome(options=options)
    
    ladbrokes.scrape(driver)
    tonybet.scrape(driver)
    unibet.scrape(driver)
    
    print('DONE SCRAPING')
    
    arbitrage_df = arbitrage.find()
    print('DONE FINDING ARBITRAGE')
    print(arbitrage_df)
    
    if arbitrage_df.empty:
        return
    
    email_list = [email1, email2]
    
    for email in email_list:
        email_sender = 'arbitragefind@gmail.com'
        email_password = password
        email_receiver = email
        
        subject = 'New arbitrage opportunity'
        body = arbitrage_df.to_string()
        # body = """
        # arbitrage
        # """
        
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)
        
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
    
if __name__ == "__main__":
    main()
