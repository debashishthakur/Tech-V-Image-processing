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
google = oauth.register(
    name = 'google',
    client_id = '',
    client_secret = '',
    access_token_url = 'https://accounts.google.com/o/oauth2/token',
    access_token_params = None,
    authorize_url = 'https://accounts.google.com/o/oauth2/auth',
    authorize_params = None,
    api_base_url = 'https://www.googleapis.com/oauth2/v1/',
    client_kwargs = {'scope' : 'openid profile email'},
)
app.secret_key = 'super secret key'
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
        case "4":
            myimage_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
     
            #Take S and remove any value that is less than half
            s = myimage_hsv[:,:,1]
            s = np.where(s < 127, 0, 1) # Any value below 127 will be excluded
 
            # We increase the brightness of the image and then mod by 255
            v = (myimage_hsv[:,:,2] + 127) % 255
            v = np.where(v > 127, 1, 0)  # Any value above 127 will be part of our mask
 
            # Combine our two masks based on S and V into a single "Foreground"
            foreground = np.where(s+v > 0, 1, 0).astype(np.uint8)  #Casting back into 8bit integer
 
            background = np.where(foreground==0,255,0).astype(np.uint8) # Invert foreground to get background in uint8
            background = cv2.cvtColor(background, cv2.COLOR_GRAY2BGR)  # Convert background back into BGR space
            foreground=cv2.bitwise_and(img,img,mask=foreground) # Apply our foreground map to original image
            # finalimage = background+foreground # Combine foreground and background
 
            imgProcessed = - background + foreground
            cv2.imwrite(f"static/{filename}", imgProcessed)
            return filename
        
        case "5":
            imgProcessed = cv2.medianBlur(img, 15)
            cv2.imwrite(f"static/{filename}", imgProcessed)
            return render_template('index2.html')

    pass
    



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    resp.raise_for_status()
    user_info = resp.json()
    # do something with the token and profile
    return redirect('/')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['POST', 'GET'])
def contact():
    return render_template('contact.html')

@app.route('/slider')
def slider():
    return render_template('slider.html', slider_value=50)

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