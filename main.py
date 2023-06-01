from flask import Flask, render_template, request, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
from authlib.integrations.flask_client import OAuth
#uploading file to static folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app = Flask(__name__)

oauth = OAuth(app)
app.secret_key = 'super secret key'
google = oauth.register(
    name = 'google',
    client_id = '859816165368-07cfe0f606bm4ncnh6nmn4jv0n4kif7h.apps.googleusercontent.com',
    client_secret = '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',
    access_token_url = 'https://accounts.google.com/o/oauth2/token',
    access_token_params = None,
    authorize_url = 'https://accounts.google.com/o/oauth2/auth',
    authorize_params = None,
    api_base_url = 'https://www.googleapis.com/oauth2/v1/',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs = {'scope' : 'profile email'},
)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

rangeValue = 0

def processImage(filename, operation):
    global rangeValue
    print(f"the operation is {operation} and filename is {filename}")
    img = cv2.imread(f"uploads/{filename}")
    match operation:
        case "1":
            imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            cv2.imwrite(f"static/{filename}", imgProcessed)
            return filename
        case "2":
            imgProcessed = cv2.Canny(img, rangeValue, 150)
            cv2.imwrite(f"static/{filename}", imgProcessed)
            print(rangeValue)
            return filename
        case "3":
            imgProcessed = cv2.medianBlur(img, 17)
            cv2.imwrite(f"static/{filename}", imgProcessed)
            return filename
        
        
        case "5":
            imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
            cv2.imwrite(f"static/{filename}", imgProcessed)
            return filename
        
        case "6":
            imgProcessed = cv2.cvtColor(img, cv2.COLOR_LRGB2LAB)
            cv2.imwrite(f"static/{filename}", imgProcessed)
            return filename
        
        case "4":
            hh, ww = img.shape[:2]

            # threshold on white
            # Define lower and uppper limits
            lower = np.array([200, 200, 200])
            upper = np.array([255, 255, 255])

            # Create mask to only select black
            thresh = cv2.inRange(img, lower, upper)

            # apply morphology
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20,20))
            morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

            # invert morp image
            mask = 255 - morph

            # apply mask to image
            imgProcessed = cv2.bitwise_and(img, img, mask=mask)

            
            cv2.imwrite(f"static/{filename}", imgProcessed)
            return filename

    pass
    



@app.route('/')
def home():
    email = dict(session).get('email', None)
    return render_template('landing.html')

@app.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    
    token = google.authorize_access_token()
    resp = google.get('userinfo', token=token)
    resp.raise_for_status()
    user_info = resp.json()
    # do something with the token and profile
    session['email'] = user_info['email']
    return render_template('index.html')


@app.route('/index')
def index():
    return render_template('index.html')




@app.route('/contact', methods=['POST', 'GET'])
def contact():
    return render_template('contact.html')



@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/edit', methods=["GET","POST"])
def edit():
    global rangeValue
    rangeValue = int(request.form.get("rangeValue"))
    # print(rangeValue)
    if request.method == "POST":
        operation = request.form.get("operation")
        if 'file' not in request.files:
            flash('No file part')
            return "error"
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            processImage(filename, operation)
            flash(f"Your image has been processed <a href='/static/{filename}' target='_blank'>here</a>")
            return render_template('index.html')
    return render_template('index.html')
    

app.run(debug=True)