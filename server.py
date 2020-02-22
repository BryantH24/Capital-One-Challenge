from flask import Flask, render_template
from flask import request


#must use static folder for images
app = Flask(__name__, static_folder=r'C:\Users\Bhou5\Desktop\yelpAPIwebsite\templates\static')

@app.route('/', methods = ['GET', 'POST'])
def form_example():
    if request.method == 'POST':  #this block is only entered when the form is submitted
        resName = request.form.get('resName')
        resLoc = request.form.get('resLoc')

        return '''<h1>The restaurant name is: {}</h1>
                  <h1>The restaurant location is: {}</h1>'''.format(resName, resLoc)

    return render_template('layout.html')
# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.debug = True
    app.run()
