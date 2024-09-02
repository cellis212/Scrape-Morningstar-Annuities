# Annuity Intelligence Data Scraper

This repository contains code to scrape individual annuity data from Morningstar's AnnuityIntel platform (https://annuityintel.com/) and processes it for further analysis.

## Project Overview

The project consists of two main components:

1. Web scraper (`scrape_annuityintel.py`)
2. Data parser (`parse_annuity_data.py`)

### Web Scraper

The web scraper uses Selenium to automate the process of logging into the AnnuityIntel platform and extracting data for multiple annuity contracts. It navigates through different tabs for each contract and saves the raw data to a CSV file.

### Data Parser

The data parser takes the raw CSV output from the web scraper and processes it into a structured JSON format. It extracts various details about each annuity contract, including contract information, surrender schedule, expenses and fees, benefits, and more and saves it as an organized JSON file.

## Requirements

- Python 3.7+
- Selenium WebDriver
- ChromeDriver
- BeautifulSoup4
- Other dependencies listed in `requirements.txt`

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/annuity-intelligence-scraper.git
   cd annuity-intelligence-scraper
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure ChromeDriver is installed and in your system PATH.

## Usage

1. Run the web scraper:
   ```bash
   python scrape_annuityintel.py
   ```
   This will generate `annuity_data.csv` with raw scraped data.

2. Parse the scraped data:
   ```bash
   python parse_annuity_data.py
   ```
   This will generate `parsed_annuities.json` with structured annuity data.

## Output

- `annuity_data.csv`: Raw scraped data from AnnuityIntel
- `parsed_annuities.json`: Structured JSON data with parsed annuity information

## Notes

- The scraper is set to extract data for contract IDs 17 through 7000. Adjust this range in `scrape_annuityintel.py` if needed.
- Login credentials are hardcoded in the script. Input your own AnnuityIntel credentials.

## Current Limitations and Future Development

Please note that the current version of this scraper does not pull the investment options part of the annuity data. This is the next step planned for development.

## Caution

Ensure you have permission to scrape data from AnnuityIntel and use the data responsibly.

## Citation

If you use this software in your research, please cite it using the following:

Ellis, C. (2024). Annuity Intelligence Data Scraper. https://github.com/cellis212/Scrape-Morningstar-Annuities

## Contributors

Cameron Ellis

## Acknowledgments

- Morningstar for providing the AnnuityIntel platform
- The Selenium and BeautifulSoup projects for their excellent web scraping tools

