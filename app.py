from flask import Flask, render_template, redirect, url_for
from flask_pymongo import PyMongo
# import scrape_mars
from scrape_mars import scrape_all
import time

app = Flask(__name__)

app.config["MONGO_URI"]="mongodb://localhost:27017/mars_app"
mongo=PyMongo(app)

@app.route("/")
def home():
# List all available api routes.
    mars=mongo.db.mars.find_one()
    return render_template("index.html", mars=mars)

@app.route("/scrape")
def scrape():
    mars=mongo.db.mars
    mars_data=scrape_mars.scrape_all()
    mars.update({}, mars_data, upsert=True)
    return "Successful"
    return redirect("/")
    
if __name__ == "__main__":
    app.run()