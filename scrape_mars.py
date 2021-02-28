from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import requests
import pymongo
import time

conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = mars_data_db
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
    browser.find_by_css("a.product-item h3")[i].click()
    sample_elem = browser.links.find_by_text('Sample').first
    hemisphere['img_url'] = sample_elem['href']
    hemisphere['title'] = browser.find_by_css("h2.title").text
    hemisphere_image_urls.append(hemisphere)
    browser.back()


    data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_image": featured_image(browser),
        "facts": html_table(),
        "henisphere_title": hemisphere_image_urls.title,
        "hemisphere_url": hemisphere_image_urls.img_url(browser)
    }

    collection.insertOne(data)
    # Stop webdriver and return data
    browser.quit()
    return data



DEFINE A FUNCTION
GO TO CHROMEDRIVER


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement=Base.classes.measurement
Station=Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

def mars_news():

    session = Session(engine)
    query = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    return jsonify(query)


def mars_feature_image():
    session = Session(engine)
    query = session.query(Measurement.station).all()
    session.close()
    return jsonify(query)


@app.route("/api/v1.0/tobs")
def tobs():

    session=Session(engine)
# Query the dates and temperature observations of the most active station for the last year of data.
    session.query(Measurement.station, func.count(Measurement.station)).group_by(
    Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    most_active_station=session.query(Measurement.tobs, Measurement.date).filter(
    Measurement.station=='USC00519281').all()
# Return a JSON list of temperature observations (TOBS) for the previous year.
    latest_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year=dt.date(2017,8,23)-dt.timedelta(days=365)
    temp_last_year=session.query(Measurement.tobs).filter(Measurement.date >=last_year).all()
    session.close()
    return jsonify(most_active_station, temp_last_year)

@app.route("/api/v1.0/<start>")
def start(start):
    session=Session(engine)
    sel =[Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    after_start = session.query(*sel).filter(Measurement.date >= start).group_by(Measurement.date).all()
    # Convert List of Tuples Into Normal List
    start_list = list(after_start)
    # Return JSON List of Min Temp, Avg Temp and Max Temp for a Given Start Range
    session.close()
    return jsonify(start_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session=Session(engine)
    sel =[Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    start_and_end = session.query(*sel).filter(Measurement.date >= start).\
            filter(Measurement.date <= end).group_by(Measurement.date).all()
        # Convert List of Tuples Into Normal List
    start_end_day_list = list(start_and_end)
        # Return JSON List of Min Temp, Avg Temp and Max Temp for a Given Start-End Range
    session.close()
    return jsonify(start_end_day_list)


if __name__ == '__main__':
    app.run(debug=True)