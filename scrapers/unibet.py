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
from datetime import date, timedelta

#driver_test = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install())) #options=options for headless

# start-up
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
    'January': '01',
    'February': '02',
    'March': '03',
    'April': '04',
    'May': '05',
    'June': '06',
    'July': '07',
    'August': '08',
    'September': '09',
    'October': '10',
    'November': '11',
    'December': '12'
}

def scrape(driver):
    site = 'https://www.unibet.com/betting/sports/filter/football/all/matches'
    driver.get(site)

    try:
        accept_cookies = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,
                                                                                    '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]')))
        accept_cookies.click()
    except:
        pass


    countries = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, '_5f930 '))) # space is intentional

    # expand country cards, if they are small enough that they haven't been expanded yet
    for country in countries:
        dimension = country.size
        if dimension.get('height') <= 48:
            country.click()
            
    # reset window to top of screen to prevent click interceptions
    driver.execute_script("window.scrollTo(0, 0);")

    # expand leagues within countries
    for country in countries:
        leagues = country.find_elements(By.CLASS_NAME, '_5f930')
        for league in leagues:
            dimension = league.size
            if dimension.get('height') <= 40:
                league.click()
                

    # load in match data
    for country in countries:
        leagues = country.find_elements(By.CLASS_NAME, '_5f930')
        
        for league in leagues:
            league_name = league.find_element(By.CLASS_NAME, '_4ec65')
            days = league.find_elements(By.CLASS_NAME, '_28843')
            
            for day in days:
                date_element = day.find_element(By.CLASS_NAME, '_6043e')
                cards = day.find_elements(By.CLASS_NAME, 'bd9c6')

                for card in cards:
                    names = card.find_elements(By.CLASS_NAME, 'ca197')
                    odds = card.find_elements(By.CLASS_NAME, '_8e013')
                    game_time = card.find_element(By.CLASS_NAME, 'a7fc8')
                    
                    # only append those with odds to record
                    if len(odds) > 2:
                        # add all but date to arrays
                        website_names.append('unibet')
                        league_names.append(league_name.text)
                        home_teams.append(names[0].text)
                        away_teams.append(names[1].text)
                        home_odds.append(odds[0].text)
                        draw_odds.append(odds[1].text)
                        away_odds.append(odds[2].text)
                        
                        # standardize date and add to array
                        if date_element.text == "Today":
                            curr_date = date.today().strftime("%d/%m/%Y")
                            new_date = game_time.text + " " + curr_date
                        elif date_element.text == "Tomorrow":
                            tomorrow_date = date.today() + timedelta(days=1)
                            tomorrow_date = tomorrow_date.strftime("%d/%m/%Y")
                            new_date = game_time.text + " " + tomorrow_date
                        else:
                            date_array = date_element.text.split()
                            new_date = game_time.text + " " + date_array[0] + "/" + months[date_array[1]] + "/" + date_array[2]
                            
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
    df.to_pickle("./scrapers/unibet.pickle")
    print(df)

#scrape(driver_test)