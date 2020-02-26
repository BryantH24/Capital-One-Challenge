from flask import Flask, render_template, jsonify
from flask import request

import requests

from yelpapi import YelpAPI

from flask_googlemaps import GoogleMaps

import os

#the number of restuarants displayed
NUM_REST = 5

#initialize app
#must use static folder for images
app = Flask(__name__, static_folder=r'\templates\static')

#opening (non-pushed) API key files
api_key = open('yelpKey.txt', 'r').read()
app.config['GOOGLEMAPS_KEY'] = open('mapsKey.txt', 'r').read()

#initialize maps
GoogleMaps(app)

class restaurant():
    def init(self, restNum, yelpJson):
        restNum = int(restNum)
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
        #self.price = yelpJson['businesses'][restNum]['price']

resObjs = ["r0", "r1", "r2", "r3", "r4"]
for res in range(0,NUM_REST):
    resObjs[res] = restaurant()

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

def initObjs(yelpJson):
    for counter in range(0,NUM_REST):
        resObjs[counter].init(counter, yelpJson)

@app.route('/', methods = ['GET', 'POST'])
def startPage():
    ipAddress = "64.189.201.73"    #for testing locally
    #ipAddress = getIP()
    locCoor = getLoc(ipAddress)
    yelp_api = YelpAPI(api_key)
    yelpJson = yelp_api.search_query(latitude = locCoor['lat'], longitude = locCoor['lon'], limit = NUM_REST, term = '')
    initObjs(yelpJson)
    if request.method == 'POST':  #this block is only entered when the form is submitted
        locCoor = getLoc(ipAddress)
        resName = request.form.get('resName')
        resLoc = request.form.get('resLoc')
        yelp_api = YelpAPI(api_key)
        yelpJson = yelp_api.search_query(latitude = locCoor['lat'], longitude = locCoor['lon'], limit = NUM_REST)


        return render_template('finalPage.html', ipA = ipAddress, latitude = locCoor['lat'], longitude = locCoor['lon'], r0=resObjs[0], r1=resObjs[1], r2=resObjs[2], r3 = resObjs[3], r4=resObjs[4])

        #return render_template('mapPage.html', image = r1.imgUrl, ipA = ipAddress, latitude = locCoor['lat'], longitude = locCoor['lon'])  #original template, do not use

    return render_template('firstPage.html',image = yelpJson['businesses'][0]['image_url'], ipA = ipAddress, latitude = locCoor['lat'], longitude = locCoor['lon'], r0=resObjs[0], r1=resObjs[1], r2=resObjs[2], r3 = resObjs[3], r4=resObjs[4])


# run the app.
if __name__ == "__main__":
    app.debug = True
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
