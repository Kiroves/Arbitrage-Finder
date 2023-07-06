# Arbitrage Finder

The Arbitrage Finder project is a useful tool for identifying arbitrage opportunities in sports betting. By scraping odds data from multiple websites and performing calculations, the project helps users find profitable arbitrage opportunities and stay informed about potential betting opportunities. 

## Prerequisites

Before running the project, make sure you have Docker installed on your machine.

## Project Structure

The project consists of the following files:

- `main.py`: The main script that orchestrates the scraping and arbitrage finding process.
- `arbitrage.py`: A module that contains functions for finding arbitrage opportunities.
- `scrapers/`: A directory containing scraper modules for different betting websites.
- `scrapers/ladbrokes.py`: A scraper module for scraping odds data from the Ladbrokes website.
- `scrapers/tonybet.py`: A scraper module for scraping odds data from the Tonybet website.
- `scrapers/unibet.py`: A scraper module for scraping odds data from the Unibet website.
- `requirements.txt`: A file specifying the project dependencies.

## How It Works

1. The `main.py` script initializes a web driver using Selenium and starts scraping odds data from multiple websites (Ladbrokes, Tonybet, Unibet) using the scraper modules.

2. The scraped data is stored in pandas DataFrames.

3. The `arbitrage.py` module contains a function `find()` that performs the arbitrage finding process. It matches similar games from different websites and calculates the arbitrage opportunities based on the odds.

4. The matched games and their corresponding arbitrage opportunities are stored in a pandas DataFrame.

5. If any arbitrage opportunities are found, the script sends an email notification to the specified email addresses, including the details of the arbitrage opportunities.

6. The script repeats the scraping and arbitrage finding process at regular intervals (e.g., every few hours) to find new arbitrage opportunities.

## Limitations

- The project assumes that the odds data on the websites being scraped is accurate and up to date. However, there may be cases where the odds change or are not accurately reflected on the websites, leading to incorrect arbitrage opportunities.
- The project currently focuses on a specific set of websites (Ladbrokes, Tonybet, Unibet) and may not work with other websites without modification.
- The project does not provide any functionality for placing bets or handling financial transactions. It is solely for informational purposes.

