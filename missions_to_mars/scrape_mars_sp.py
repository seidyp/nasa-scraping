# Import Splinter, BeautifulSoup, and Pandas
from bs4 import BeautifulSoup
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import requests
import pymongo

def init_browser():
    # Path to chromedriver - Set the executable path and initialize the chrome browser in splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    
    return Browser('chrome', **executable_path, headless=True)


def scrape_info():    
    browser = init_browser()

    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)

    db = client.mars_db

    mars_result = []

    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(url)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    title_results = soup.find_all("li", class_=["slide"])
    title = title_results[0].find("div", class_=["content_title"]).text

    # .find() the paragraph text
    paragraph_text = soup.find(class_="article_teaser_body").text

    mars_result = {
        "title": title,
        "text": paragraph_text
    }
    db.mars_db.insert_one(mars_result)


    ## JPL Space Images Featured Image
    # Visit JPL space images Mars URL 
    jpl_url = "https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html"
    browser.visit(jpl_url)

    # Find and click the full image button - must be in all caps
    browser.links.find_by_partial_text('FULL').click()

    jpl_html = browser.html
    jpl_soup = BeautifulSoup(jpl_html, 'html.parser')

    # find the image url
    header_img = jpl_soup.find_all('div', class_='floating_text_area')[0].find('a')['href']

    header_img

    base_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/'

    # Use the base url to create an absolute url
    img_url = f'{base_url}{header_img}'

    img_title = "Featured Image"
    img_text = "Featured Image"

    mars_result = {
        "title": img_title,
        "text": img_text,
        "link": img_url
    }
    db.mars_db.insert_one(mars_result)


    ## Mars Facts

    # Create a dataframe from the space-facts.com mars page
    mars_facts_url = 'https://space-facts.com/mars/'

    mars_table = pd.read_html(mars_facts_url)
    mars_df = mars_table[0]

    # clean the dataframe and export to HTML
    mars_df_columns = mars_df.rename(columns={0:"Attribute", 1:"Information"})
    len(mars_df_columns)

    for row in range(0, len(mars_df_columns)):
        mars_result_inner = {
            "attribute": mars_df_columns["Attribute"][row],
            "information": mars_df_columns["Information"][row]
        }
        db.mars_db.insert_one(mars_result_inner)

    ## Hemispheres

    # visit the USGS astrogeology page for hemisphere data from Mars
    hemi_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    browser.visit(hemi_url)

    hemi_html = browser.html
    hemi_soup = BeautifulSoup(hemi_html, 'html.parser')

    # finding length of all divs in hemisphere for list
    num_of_hemi = len(hemi_soup.find_all('div', class_='item'))

    # lists to append to:
    hemi_hrefs = []

    # for loop to extract information

    for i in range(0,num_of_hemi):
        
        # navigating browser remotely and creating partial_text to search for with click
        partial_text = hemi_soup.find_all('div', class_='item')[i].text[0:15]
        browser.links.find_by_partial_text(partial_text).click()
        inner_html = browser.html
        inner_soup = BeautifulSoup(inner_html, 'html.parser')
        
        # finding hrefs and appending to list
        inner_href = inner_soup.find('div', class_='downloads').find('li').find('a')['href']
        
        # finding titles and appending to list
        inner_title = inner_soup.find('h2', class_='title').text
        
        mars_result = {
            'hemisphere': inner_title,
            'hemi_url': inner_href
        }
        
        db.mars_db.insert_one(mars_result)


        hemi_hrefs.append(mars_result)
                
        # navigating back to browser
        browser.back()

    browser.quit()

    return mars_result

    



