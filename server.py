from flask import Flask, render_template, jsonify, url_for
from flask import request

import requests

from yelpapi import YelpAPI

from flask_googlemaps import GoogleMaps

import os

#the number of restuarants displayed, can be increased with edits in html
NUM_REST = 5

#initialize app
#must use static folder for images
app = Flask(__name__, static_url_path='/static')

#opening (non-pushed) API key files
api_key = open('yelpKey.txt', 'r').read()
app.config['GOOGLEMAPS_KEY'] = open('mapsKey.txt', 'r').read()

#initialize maps
GoogleMaps(app)

#class parses information from json, makes template easier to use
class restaurant():
    def init(self, restNum, yelpJson):
        self.name = yelpJson['businesses'][restNum]['name']
        self.url = yelpJson['businesses'][restNum]['url']
        self.imgUrl = yelpJson['businesses'][restNum]['image_url']
        self.phoneNum = yelpJson['businesses'][restNum]['phone']
        self.lat = yelpJson['businesses'][restNum]['coordinates']['latitude']
        self.long = yelpJson['businesses'][restNum]['coordinates']['longitude']
        self.category = yelpJson['businesses'][restNum]['categories'][0]['title']
        self.rate = yelpJson['businesses'][restNum]['rating']
        self.revNum = yelpJson['businesses'][restNum]['review_count']
        self.distance = format(yelpJson['businesses'][restNum]['distance'] / 1609, '7.2f')
        self.price = yelpJson['businesses'][restNum]['price']

#on run, creates array of restaurant objects
resObjs = ["r0", "r1", "r2", "r3", "r4"]
for res in range(0,NUM_REST):
    resObjs[res] = restaurant()

#gets location from ip using ip-api call
def getLoc(ipAddress):
    try:
        response = requests.get("http://ip-api.com/json/{}".format(ipAddress))
        js = response.json()
        return js
    except Exception as e:
        return "Unknown"

def getIP():
    if request.headers.getlist("X-Forwarded-For"):
       ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
       ip = request.remote_addr
    return ip
#initializes all objects at same time
def initObjs(yelpJson, NUM_REST):
    for counter in range(0,NUM_REST):
        resObjs[counter].init(counter, yelpJson)
#makes sure that there are 4 restaurants in yelp output
def checkResults(yelpJson):
    try:
        yelpJson['businesses'][4]['name']
    except IndexError:
        return -1

@app.route('/', methods = ['GET', 'POST'])
def startPage():
    yelp_api = YelpAPI(api_key)
    #ipAddress = "64.189.201.73"    #for testing locally
    ipAddress = getIP()           #for deployment
    locCoor = getLoc(ipAddress)
    yelpJson = yelp_api.search_query(latitude = locCoor['lat'], longitude = locCoor['lon'], limit = NUM_REST)
    initObjs(yelpJson, 5)
    if request.method == 'POST':  #this block is only entered when the form is submitted
        #read in form values
        queryIn = request.form.get('query')
        locationIn = request.form.get('location')
        distanceIn = request.form.get('distance')
        priceIn = str(int(request.form.get('price')) -1)
        #search with form values
        yelpJson = yelp_api.search_query(term = queryIn, location = locationIn, distance = distanceIn, price = priceIn, limit = NUM_REST)
        if checkResults(yelpJson)==-1: #if the search is too specific
            return '<h1> Your search did not return enough restaurants to display, please try again</h1><a href = "/" class = "w3-xlarge w3-button ">Clear Search</a>'
        initObjs(yelpJson, 5)
        #render page after search using values from form
        return render_template('finalPage.html',
                                ipA = ipAddress,
                                term = queryIn,
                                mapR = distanceIn,
                                latitude = yelpJson['region']['center']['latitude'],
                                longitude = yelpJson['region']['center']['longitude'],
                                r0=resObjs[0],
                                r1=resObjs[1],
                                r2=resObjs[2],
                                r3 = resObjs[3],
                                r4=resObjs[4])
    #render page before search with defaults and ip location
    return render_template('firstPage.html',
                            ipA = ipAddress,
                            latitude = locCoor['lat'],
                            longitude = locCoor['lon'],
                            r0=resObjs[0],
                            r1=resObjs[1],
                            r2=resObjs[2],
                            r3 = resObjs[3],
                            r4=resObjs[4])
@app.route('/moreResults')
def moreResults():
    yelp_api = YelpAPI(api_key)
    #ipAddress = "64.189.201.73"
    ipAddress = getIP()     #for testing locally
    locCoor = getLoc(ipAddress)
    if len(resObjs) < 9:
        for objectNameMaker in range(5, 10):  #should prob put into a function
            resObjs.append('r' + str(objectNameMaker))
            resObjs[objectNameMaker] = restaurant()
    NUM_REST = 10
    yelpJson = yelp_api.search_query(latitude = locCoor['lat'], longitude = locCoor['lon'], limit = 10)
    initObjs(yelpJson, 10)
    return render_template('moreResults.html', resObjs = resObjs)

# run the app.
if __name__ == "__main__":
    app.debug = True
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
