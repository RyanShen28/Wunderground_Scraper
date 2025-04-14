import requests
import csv
import lxml.html as lh
from lxml import etree
import config
from util.Metric_Imperial_Converter import convert
from util.Parser import Parser
from util.Utils import Utils
import asyncio
from playwright.async_api import async_playwright, Playwright, TimeoutError, Error







# configuration
stations_file = open('station_ids.txt', 'r')
station_ids = stations_file.readlines()
interval = input("Please give minimum duration between readings, in minutes. Duration cannot exceed 1 day.")
if (not interval.isnumeric()) or (int(interval)<=0 or int(interval) >=1440):
    raise ValueError("Value must be between 0 and 1 day")
interval = int(interval)
# Date format: YYYY-MM-DD

day_step = input("How many days in between recordings do you want? Duration cannot exceed 100 days.")
if (not day_step.isnumeric()) or (int(day_step)<0 or int(day_step) >=1440):
    raise ValueError("Value must be between 0 and 100 days")
day_step = int(day_step)+1

START_DATE = config.START_DATE
END_DATE = config.END_DATE

UNITS = config.UNITS
session = requests.Session()
timeout = 5
Limit = 24
sem = asyncio.Semaphore(Limit)
converter = convert(UNITS)


async def fetch(browser, url, date, sem, results):
    async with sem:
        try:

            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_selector('#inner-content > div.region-content-main > div.row > div:nth-child(5) > div:nth-child(1) > div > lib-city-history-observation > div > div.observation-table > table > thead > tr > th.mat-sort-header.mat-mdc-header-cell.mdc-data-table__header-cell.cdk-header-cell.cdk-column-dateString.mat-column-dateString',timeout=5000)
            content = await page.content()
            html_data_table=lh.fromstring(content).xpath('/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[2]/section/div[2]/div[1]/div[5]/div[1]/div/lib-city-history-observation/div/div[2]/table/tbody')
            data_rows = Parser.parse_html_table(interval, date, html_data_table)
            data_to_write = converter.clean_and_convert(data_rows)
            results.append(data_to_write)
            print(f"date was {date}")
            await page.close()
        except TimeoutError:
            print("No data on this day / Timeout Error")
            print(date)
            await page.close()
        except Error as e:
            if "net::ERR_NETWORK_CHANGED" in str(e):
                print("Network change detected, retry fetch")
                await page.close()
                await asyncio.sleep(3)
                await fetch(browser, url, date, sem, results)
            else:
                print("Unknown error")
                await page.close()


async def scrape(url):

    #definitions
    session = requests.Session()
    global START_DATE
    global END_DATE
    global UNITS
    Timeout_flag = False
    file_name = f'{url.split("/")[-2]}.csv'
    date_url_list = Utils.date_url_generator(url, START_DATE, END_DATE, day_step)

    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        tasks = [fetch(browser, url, date, sem, results) for date, url in date_url_list]
        await asyncio.gather(*tasks)
        await browser.close()

    with open(file_name, 'a+', newline='') as csvfile:
        fieldnames = ['Date', 'Time',	'Temperature',	'Dew_Point', 'Humidity','Wind',	'Wind_Speed',	'Gust', 'Pressure', 'Precip_Rate',	'Condition']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if UNITS == "metric":
            writer.writerow({'Date': 'Date', 'Time': 'Time', 'Temperature': 'Temperature_C', 'Dew_Point': 'Dew_Point_C', 'Humidity': 'Humidity_%',	'Wind': 'Wind Direction',	'Wind_Speed': 'Speed in km/h',	'Gust': 'Gust km/h', 'Pressure': 'Pressure in hPa',	'Precip_Rate': 'Precipitation Rate in mm', 'Condition' : 'Condition'})
        elif UNITS == "imperial": 
            writer.writerow({'Date': 'Date', 'Time': 'Time', 'Temperature': 'Temperature_F', 'Dew_Point': 'Dew_Point_F',	'Humidity': 'Humidity_%',	'Wind': 'Wind Direction',	'Wind_Speed': 'Speed in mp/h',	'Gust': 'Gust mp/h',	'Pressure': 'Pressure in inHg',	'Precip_Rate': 'Precipitation Rate in inches',	'Condition': 'Condition',})
        else:
            raise Exception("UNITS must be metric or imperial")
        for entry in results:
            try:
                print(f' {len(entry)} rows saved from {url}, {entry[0]["Date"]}')
                writer.writerows(entry)
            except Exception as e:
                print(e)


async def main():


    for url in station_ids:
        url = url.strip()
        title = lh.fromstring(session.get(f'https://wunderground.com/weather/{url}', timeout=timeout).content).xpath('//title')[0].text #should give Choteau, MT
        city = title.split(",")[0].lower().replace(" ", "-")
        state = title.split(",",1)[1][1:3].lower()
        url = f'https://wunderground.com/history/daily/us/{state}/{city}/{url}/date'

        await scrape(url)

if __name__ == "__main__":
    asyncio.run(main())
