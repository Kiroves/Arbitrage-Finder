#import libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import *
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

#driver_test = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

def scrape(driver):
    # start-up
    site = 'https://tonybet.com/ca/prematch'
    driver.get(site)

    # accept cookies and click the soccer tab
    try:
        accept_cookies = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH,
                                                                                    '//*[@id="platform"]/div/div[3]/div/button')))
        accept_cookies.click()
        
        soccer_btn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH,
                                                                                    '//*[@id="platform"]/div/div[2]/div/div[2]/div/div/div/div[2]/div/div[2]/div[1]/div/div/div/div/div/div/div[1]')))
        soccer_btn.click()
    except:
        pass

    
    events_holder = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'events-holder ')))
    event_tables = WebDriverWait(events_holder, 10).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'event-table')))

    website_names = []
    league_names = []
    dates = []
    home_teams = []
    away_teams = []
    home_odds = []
    draw_odds = []
    away_odds = []

    for table in event_tables:
        # scroll down the height of the table, needed to load data
        table_height = table.size.get("height")
        driver.execute_script("window.scrollBy(0, " + str(table_height) + ");")
        
        league_name = WebDriverWait(table, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'event-table__title-text')))
        rows = WebDriverWait(table, 10).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'event-table__row')))
        
        for row in rows:
            date = row.find_element(By.CLASS_NAME, 'event-table-body-module_date__-cmdj')
            teams = row.find_elements(By.CLASS_NAME, 'event-table__team-name')
            odds = row.find_elements(By.CSS_SELECTOR, 'div.table-outcome-module_content__1ycSD')
            
            # check that there are enough odds cards to make a full table row
            if len(odds) > 2: # REFACTOR, POTENTIAL ERROR WHEN THE FIRST THREE ODDS ARE NOT THE ONES SCRAPED
                # add all data to arrays except date
                website_names.append('tonybet')
                league_names.append(league_name.text)
                home_teams.append(teams[0].text)
                away_teams.append(teams[1].text)
                home_odds.append(odds[0].text)
                draw_odds.append(odds[1].text)
                away_odds.append(odds[2].text)
                
                # standardize date and add to array
                date_array = date.text.split()
                date_array[0] = date_array[0].replace('.', '/')
                
                # convert to 24 hour time if needed
                if date_array[2] == 'PM':
                    time_array = date_array[1].split(':')
                    hour = int(time_array[0]) + 12
                    new_time = str(hour) + ":" + time_array[1]
                else:
                    new_time = date_array[1]
                    
                new_date = new_time + " " + date_array[0]
                dates.append(new_date)
                        
    dataset = {
        'website' : website_names,
        'league' : league_names,
        'date' : dates,
        'home' : home_teams,
        'away' : away_teams,
        'home_odds' : home_odds,
        'draw_odds' : draw_odds,
        'away_odds' : away_odds
    }

    df = pd.DataFrame(dataset)
    df.to_pickle("./scrapers/tonybet.pickle")
    print(df)

#scrape(driver_test)