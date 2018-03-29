# Dependencies
from flask import Flask, render_template, redirect
import pymongo
import scrape_mars

# Create a Flask app
app = Flask(__name__)

# Connect to MongoDB
conn = "mongodb://localhost:27017"
client = pymongo.MongoClient(conn)

# Use database and create it if it does not exist
db = client.martiansDB
  

# Create index route
@app.route("/")
def index():

    # old mars data is stored in a different collection, to visualize the changes between
    # newly scraped data and previous data
    old_mars_data = db.old_mars_collection.find_one()
    # Render html
    return render_template("index.html", mars_data=old_mars_data, text="Previous stored data in mongoDB: ")

@app.route("/scrape")
def scrape():
    scraped_data = scrape_mars.scrape()
    db.mars_collection.update(
        {},
        scraped_data,
        upsert=True
    )
    mars_data = db.mars_collection.find_one()
    #return redirect("http://localhost:5000/", code=302)
    return render_template("index.html", mars_data=mars_data, text="Newly Scraped Data: ")


if __name__ == "__main__":
    app.run(debug=True)