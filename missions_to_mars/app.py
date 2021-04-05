from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars_sp
import pymongo

# Create an instance of Flask
app = Flask(__name__)

# Use PyMongo to establish Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_db")
mars_db = mongo.db.mars_db

# Route to render index.html template using data from Mongo
@app.route("/")
def home():
    mars_data = mongo.db.mars_db.find_one()
    # Return template and data
    return render_template("index.html", mars_data=mars_data)


# Route that will trigger the scrape function
@app.route("/scrape")
def scrape():

    # Run the scrape function
    mars_data2 = scrape_mars_sp.scrape_info()

    # Update the Mongo database using update and upsert=True
    mars_db.update({}, mars_data2, upsert=True)

    # Redirect back to home page
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
