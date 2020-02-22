from flask import Flask, render_template, jsonify
from flask import request

import requests

from yelpapi import YelpAPI


api_key = ""
#must use static folder for images
app = Flask(__name__, static_folder=r'\templates\static')

def getLoc(ipAddress):
    try:
        response = requests.get("http://ip-api.com/json/{}".format(ipAddress))
        js = response.json()
        return js
    except Exception as e:
        return "Unknown"


@app.route('/', methods = ['GET', 'POST'])
def startPage():
    ipAddress = "64.189.201.73"
    locCoor = getLoc(ipAddress)
    if request.method == 'POST':  #this block is only entered when the form is submitted
        resName = request.form.get('resName')
        resLoc = request.form.get('resLoc')
        yelp_api = YelpAPI(api_key)
        yelpJson = yelp_api.search_query(latitude = locCoor['lat'], longitude = locCoor['lon'])
        #yelpJson = requests.get(url = r"https://api.yelp.com/v3/businesses/search", headers = header,  params = latLongSend)
        return '''<h1>The restaurant name is: {}</h1>
                  <h1>Your Latitiude is: {}</h1>
                  <h1>Your Longtitiude is: {}</h1>
                  <h1>Yelp data: {}</h1>'''.format(resName, locCoor['lat'], locCoor['lon'], str(yelpJson))

    return render_template('layout.html')


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.debug = True
    app.run()
