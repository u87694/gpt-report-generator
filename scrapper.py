import requests
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import time
import csv
# selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
import configparser
import os, sys

csv.field_size_limit(sys.maxsize)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

config = configparser.ConfigParser()
config.read('config.ini')

MAX_SEARCH_RESULT = config.get('SCRAPPER', 'MAX_SEARCH_RESULT')
CSV_FILE_NAME = config.get('SCRAPPER', 'CSV_FILE_NAME')

failed_urls = set()

def search(ddgs, queries):
    # Scrape articles from web, ignore already scrapped documents
    # urls = [r['href'] for r in ddgs.text(str(string), max_results=6)]
    urls = set()
    for query in queries:
        search_results = ddgs.text(query, max_results=int(MAX_SEARCH_RESULT))
        for r in search_results:
            urls.add(r['href'])
    return urls


def scrape_with_selenium(url):
    print(f'\tDriver:')
    # auto install and configure chromedriver
    chromedriver_autoinstaller.install()

    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    title = soup.title.text.strip() if soup.title else "No Title Found"
    content = ' '.join([p.text.strip() for p in soup.find_all('p')])
    print(f'\tTitle: {title}')
    print(f'\tContent: {content[0:20]}...')

    return (title, content)

def scrape(url):
    # Scrape articles
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.text.strip() if soup.title else "No Title Found"
        content = ' '.join([p.text.strip() for p in soup.find_all('p')])
        print()

        if content == '':
            print('**Unable to scrape retrying with Chrome**')
            # scrape using chromedriver
            title, content = scrape_with_selenium(url)
        else:
            print(f'Title: {title}')
            print(f'Content: {content[0:200]}...')

        if url in failed_urls:
            failed_urls.remove(url)

        return (title, content)
    except requests.exceptions.RequestException as e:
        print(f'Error: {e}')
        failed_urls.add(url)


def build_knowledgebase(urls):
    # Download articles and save as CSV
    urls = list(urls)
    for i in range(len(urls)):
        print(f'\n#{i+1} Scrapping url: {urls[i]}')
        try:
            if not os.path.exists(CSV_FILE_NAME):
                with open(CSV_FILE_NAME, 'w'):
                    pass
            title, content = scrape(urls[i])
            with open(CSV_FILE_NAME, 'a', newline='', encoding='utf-8') as csv_file:
                fieldnames = ['SrNo', 'Url', 'Title', 'Content']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                if csv_file.tell() == 0:
                    writer.writeheader()
                writer.writerow({'SrNo': i+1, 'Url': urls[i], 'Title': title, 'Content': content})
                print(f'\nSaved Article {i+1} into csv')
        except Exception as e:
            print(f'Skipped saving\nError:\n{e}')
        print()
        print('---------------------------------------------------------------------------')


def start():
    start = time.time()

    ddgs = DDGS()
    # search for articles on web
    queries = [
        "Canoo size, growth rate, trends and key players in the industry",
        "detail analysis of Canoo's main competitors",
        "trends in electric vehicle industry, consumer perspective, advancements etc.",
        "Canoo's financial performance"
    ]
    print(f"Initialiing, querying through web...")
    urls = search(ddgs, queries)

    # build knowledgebase
    print(f'Found {len(urls)} documents, initializing scrapping')
    build_knowledgebase(urls)

    # retry for failed urls
    if len(failed_urls) > 0:
        print(f'\n{len(failed_urls)} urls failed, retrying once to scrape failed urls')
        build_knowledgebase(failed_urls)

    end = time.time()
    elapsed_time = end - start

    if elapsed_time >= 60:
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        time_taken = f"{minutes} min, {seconds} sec"
    else:
        seconds = int(elapsed_time)
        time_taken = f"{seconds} sec"
    print(f"Script finished in {time_taken}\nSkipped {len(failed_urls)} urls.")
