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
from datetime import date
import time

#driver_test = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# initalize arrays
website_names = []
league_names = []
dates = []
home_teams = []
away_teams = []
home_odds = []
draw_odds = []
away_odds = []

# for date standardizing
months = {
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12'
}

tab = 'Today'

# convert a string fraction into a decimal float
def fraction_to_decimal(fraction):
    numerator, denominator = fraction.split('/')
    return int(numerator) / int(denominator)
    
def expand_cards(leagues, driver):
    for league in leagues:     
        dimension = league.size
        league_height = dimension.get('height')
                    
        # click the odds cards if they are small enough that they have not been expanded yet
        if league_height <= 36:
            try:
                league.click()
            except ElementClickInterceptedException:
                accept_cookies = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH,
                                                                                        '//*[@id="onetrust-accept-btn-handler"]')))
                accept_cookies.click()
                league.click()
                    
def get_data(leagues):
    # loop through leagues again, scraping the data this time
    for league in leagues:
        odds_cards = WebDriverWait(league, 30, ignored_exceptions=[StaleElementReferenceException]).until(EC.visibility_of_any_elements_located((By.CLASS_NAME, 'sport-card'))) #still timing out here
        league_name = WebDriverWait(league, 30, ignored_exceptions=[StaleElementReferenceException]).until(EC.visibility_of_element_located((By.CLASS_NAME, 'header-title')))
        
        for odds_card in odds_cards:
            date_element = odds_card.find_element(By.CLASS_NAME, 'sport-card-label')

            names = odds_card.find_elements(By.CLASS_NAME, 'flag-sp')
            odds_buttons = odds_card.find_elements(By.CLASS_NAME, 'sport-card-btn-wrapper')
            home_odd = odds_buttons[0].text
            draw_odd = odds_buttons[1].text
            away_odd = odds_buttons[2].text
            
            # check that all odds buttons contain valid data
            if '/' in home_odd and '/' in draw_odd and '/' in away_odd:
                # convert fractions to decimals
                home_odd = fraction_to_decimal(home_odd)
                draw_odd = fraction_to_decimal(draw_odd)
                away_odd = fraction_to_decimal(away_odd)
                
                # add everything except the date to arrays
                website_names.append('ladbrokes')
                league_names.append(league_name.text)
                home_teams.append(names[0].text)
                away_teams.append(names[1].text)
                home_odds.append(home_odd)
                draw_odds.append(draw_odd)
                away_odds.append(away_odd)
                
                # standardize date and add to array
                date_text = date_element.text
                date_array = date_text.split()
                if date_array[1] == "Today":
                    date_array[1] = date.today().strftime("%d/%m/%Y")
                else:
                    month_name = date_array[2]
                    month_num = months[month_name]
                    
                    # deal with new years
                    if date.today().month == 12 and month_name == "Jan":
                        year = date.today().year + 1
                    else:
                        year = date.today().year
                        
                    date_array[1] = date_array[1] + "/" + month_num + "/" + str(year)
                    
                new_date = date_array[0] + " " + date_array[1]
                dates.append(new_date)
        
# scrape any one of the three tabs on ladbrokes website
def scrape_tab(driver):
    sports_matches_tab = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                                                '#content > sport-main-component > div.page-inner > div > sport-matches-page > sport-matches-tab')))
    
    # in this case there are no events that day
    if sports_matches_tab.text == 'No events found' and tab == 'Today':
        return
    
    leagues = WebDriverWait(sports_matches_tab, 15, ignored_exceptions=[StaleElementReferenceException]).until(EC.visibility_of_all_elements_located((By.XPATH, 'accordion')))

    tries = 0
    while tries < 4:
        try:
            expand_cards(leagues, driver)
            break
        except StaleElementReferenceException:
            if tries < 3:
                print('failed to expand cards')
                tries += 1
                continue
            else:
                raise
    
    tries = 0
    while tries < 4:
        try:
            get_data(leagues)
            break
        except StaleElementReferenceException:
            if tries < 3:
                print('failed to get data')
                tries += 1
                continue
            else:
                raise

# scrape all the tabs on ladbrokes website
def scrape(driver):
    # load site
    site = 'https://sports.ladbrokes.com/sport/football/matches/today'
    driver.get(site)
    
    global tab
    # loop through each tab on site
    for i in range(3):
        if i == 0:
            time.sleep(2)
            scrape_tab(driver)
        elif i == 1:
            # click tomorrow tab
            tab = 'Tomorrow'
            tomorrow = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/sport-main-component/div[2]/div/sport-matches-page/filter-buttons/div/a[2]')))
            driver.execute_script("arguments[0].click();", tomorrow)
            driver.execute_script("window.scrollTo(0, 0);")
            scrape_tab(driver)
        else:
            #click future tab
            tab = 'Future'
            future = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/sport-main-component/div[2]/div/sport-matches-page/filter-buttons/div/a[3]')))
            driver.execute_script("arguments[0].click();", future)
            driver.execute_script("window.scrollTo(0, 0);")
            scrape_tab(driver)

    
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
    df.to_pickle("./scrapers/ladbrokes.pickle")
    print(df)

#scrape(driver_test)