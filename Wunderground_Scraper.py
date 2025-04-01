import requests
import csv
import lxml.html as lh
from lxml import etree
import config
from util.Metric_Imperial_Converter import convert
from util.Parser import Parser
from util.Utils import Utils
from playwright.sync_api import sync_playwright
p = sync_playwright().start()
browser = p.chromium.launch(headless=False)






# configuration
stations_file = open('station_ids.txt', 'r')
station_ids = stations_file.readlines()
interval = input("Please give minimum duration between readings, in minutes. Duration cannot exceed 1 day.")
if (not interval.isnumeric()) or (int(interval)<=0 or int(interval) >=1440):
    raise ValueError("Value must be between 0 and 1 day")
interval = int(interval)
# Date format: YYYY-MM-DD
START_DATE = config.START_DATE
END_DATE = config.END_DATE

UNITS = config.UNITS
# find the first data entry automatically
FIND_FIRST_DATE = config.FIND_FIRST_DATE
session = requests.Session()
timeout = 5


def scrape(url):
    session = requests.Session()
    global START_DATE
    global END_DATE
    global UNITS
    file_name = f'{url.split("/")[-2]}.csv'
    date_url_list = Utils.date_url_generator(url, START_DATE, END_DATE)

    with open(file_name, 'a+', newline='') as csvfile:
        fieldnames = ['Date', 'Time',	'Temperature',	'Dew_Point', 'Humidity','Wind',	'Wind Speed',	'Wind Gust', 'Pressure', 'Precip.',	'Condition']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if UNITS == "metric":
            writer.writerow({'Date': 'Date', 'Time': 'Time', 'Temperature': 'Temperature_C', 'Dew_Point': 'Dew_Point_C', 'Humidity': 'Humidity_%',	'Wind': 'Wind Direction',	'Wind Speed': 'Speed in km/h',	'Wind Gust': 'Gust km/h', 'Pressure': 'Pressure in hPa',	'Precip.': 'Precipitation Rate in mm', 'Condition' : 'Condition'})
        elif UNITS == "imperial": 
            writer.writerow({'Date': 'Date', 'Time': 'Time', 'Temperature': 'Temperature_F', 'Dew_Point': 'Dew_Point_F',	'Humidity': 'Humidity_%',	'Wind': 'Wind Direction',	'Wind Speed': 'Speed in mp/h',	'Gust': 'Gust mp/h',	'Pressure': 'Pressure in inHg',	'Precip.': 'Precipitation Rate in inches',	'Condition': 'Condition',})
        else:
            raise Exception("UNITS must be metric or imperial")
        
        for dates, url in date_url_list:
            try:
                html_data_table = False
                while not html_data_table:
                    page = browser.new_page()
                    page.goto(url, timeout = 30000, wait_until="domcontentloaded")

                    page.wait_for_selector('#inner-content > div.region-content-main > div.row > div:nth-child(5) > div:nth-child(1) > div > lib-city-history-observation > div > div.observation-table.ng-star-inserted > table > thead')

                    html_string = page.content()
                    doc = lh.fromstring(html_string)
                    page.close()

                    html_data_table = doc.xpath('/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[2]/section/div[2]/div[1]/div[5]/div[1]/div/lib-city-history-observation/div/div[2]/table/tbody')
                data_rows = Parser.parse_html_table(interval, dates, html_data_table)
                #conversions done here
                converter = convert(UNITS)
                data_to_write = converter.clean_and_convert(data_rows)
                    
                print(f' {len(data_to_write)} rows saved from {url}.')
                writer.writerows(data_to_write)
            except Exception as e:
                print(e)



for url in station_ids:
    url = url.strip()
    title = lh.fromstring(session.get(f'https://wunderground.com/weather/{url}', timeout=timeout).content).xpath('//title')[0].text #should give Choteau, MT
    city = title.split(",")[0].lower().replace(" ", "-")
    state = title.split(",",1)[1][1:3].lower()
    url = f'https://wunderground.com/history/daily/us/{state}/{city}/{url}/date'
    #print(url)
    #exit()
    #print(url)

    scrape(url)