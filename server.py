from flask import Flask, render_template, jsonify
from flask import request

import requests

from yelpapi import YelpAPI

from flask_googlemaps import GoogleMaps

import os
api_key = open('yelpKey.txt', 'r').read()
#must use static folder for images
app = Flask(__name__, static_folder=r'\templates\static')
app.config['GOOGLEMAPS_KEY'] = open('mapsKey.txt', 'r').read()
GoogleMaps(app)

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


@app.route('/', methods = ['GET', 'POST'])
def startPage():
    #ipAddress = "64.189.201.73"    #for testing locally
    ipAddress = getIP()
    locCoor = getLoc(ipAddress)
    if request.method == 'POST':  #this block is only entered when the form is submitted
        resName = request.form.get('resName')
        resLoc = request.form.get('resLoc')
        yelp_api = YelpAPI(api_key)
        yelpJson = yelp_api.search_query(latitude = locCoor['lat'], longitude = locCoor['lon'], limit = 1)

        # return '''<h1>The restaurant name is: {}</h1>
        #           <h1>Your Latitiude is: {}</h1>
        #           <h1>Your Longtitiude is: {}</h1>
        #           <p>Yelp data: {}</p>
        #           <div>
        #           {{googlemap("please_work", lat=32.9636, lng=-96.7468, markers=[(-96.7468, 32.9636)]}}
        #           </div>
        #           <img src = {}>'''.format(resName, locCoor['lat'], locCoor['lon'], str(yelpJson), yelpJson['businesses'][0]['image_url'])


        #return '<h1>{}</h1>'.format(str(ip))

        return render_template('finalPage.html',image = yelpJson['businesses'][0]['image_url'], ipA = ipAddress, latitude = locCoor['lat'], longitude = locCoor['lon'] )

        return render_template('mapPage.html', image = yelpJson['businesses'][0]['image_url'], ipA = ipAddress, latitude = locCoor['lat'], longitude = locCoor['lon'])

    return render_template('layout.html')


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.debug = True
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
