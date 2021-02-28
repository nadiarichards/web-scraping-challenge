import pandas as pd
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import requests
import pymongo
import time

# conn = 'mongodb://localhost:27017'
# client = pymongo.MongoClient(conn)
# db = mars_data_db
# time_delay = randint(3,6)

# collection.insertOne(data)

def scrape_all():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    mars_url = 'https://mars.nasa.gov/news/'
    browser.visit(mars_url)
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)
    news_html = browser.html
    news_soup = soup(news_html, 'html.parser')
    slide_elem = news_soup.select_one('ul.item_list li.slide')
    news_title = slide_elem.find("div", class_='content_title').get_text()
    news_p = slide_elem.find('div', class_="article_teaser_body").get_text()

    url_image = "https://www.jpl.nasa.gov/images/"
    browser.visit(url_image)
    img_html = browser.html
    img_soup = soup(img_html, 'html.parser')
    header=img_soup.find("h2", class_="mb-3 text-h5").text
    endpoint=header.replace(' ', '-').lower()
    url_featured=url_image = "https://www.jpl.nasa.gov/images/" + endpoint
    browser.visit(url_featured)
    featured_html = browser.html
    featured_soup = soup(featured_html, 'html.parser')
    featured_image=featured_soup.find('img', class_='BaseImage object-scale-down')['data-src']

    table_url="https://space-facts.com/mars/"
    tables = pd.read_html(table_url)
    df=tables[1]
    mars_df=df[["Mars - Earth Comparison", "Mars"]]
    mars_df.columns = ['Description','Value']
    mars_df.set_index('Description',inplace=True)
    html_table=mars_df.to_html()

    hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemisphere_url)
    hemisphere_image_urls = []
    links = browser.find_by_css("a.product-item h3")
    for i in range(len(links)):
        hemisphere = {}
        time.sleep(2)
        browser.find_by_css("a.product-item h3")[i].click()
        sample_elem = browser.links.find_by_text('Sample').first
        hemisphere['img_url'] = sample_elem['href']
        hemisphere['title'] = browser.find_by_css("h2.title").text
        hemisphere_image_urls.append(hemisphere)
        hemisphere_titles=[sub['title'] for sub in hemisphere_image_urls]
        hemisphere_urls=[sub['img_url'] for sub in hemisphere_image_urls]
        browser.back()


    data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_image": featured_image,
        "facts": html_table,
        "hemisphere_title": hemisphere_titles,
        "hemisphere_urls": hemisphere_urls
    }

    # collection.insertOne(data)
    # Stop webdriver and return data
    browser.quit()
    return data