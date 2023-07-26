from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import pyrebase
import os
import pleasework as backend
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'




UPLOAD_FOLDER = 'static/Upload_Folder'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
firebaseConfig = {
  "apiKey": "AIzaSyB0vxSbpKCNIhsiViznwYa-EM2vXqUVBbs",
  "authDomain": "daniels-meet-project.firebaseapp.com",
  "databaseURL": "https://daniels-meet-project-default-rtdb.europe-west1.firebasedatabase.app",
  "projectId": "daniels-meet-project",
  "storageBucket": "daniels-meet-project.appspot.com",
  "messagingSenderId": "504431140017",
  "appId": "1:504431140017:web:0b9f4e48dd371631909690",
  "measurementId": "G-M4RBF4755D"
}
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/' , methods=['GET' , 'POST'])
def home():
    return render_template("index.html")

@app.route('/homePage')
def homepage():
    return render_template("home.html")

@app.route('/login' , methods=['GET' , 'POST'])
def login():
    if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            try:
                login_session['user'] = auth.sign_in_with_email_and_password(email , password)
                uname = db.child("Users").child(login_session['user']['localId']).get().val()
                login_session['uname'] = uname['username']
                return redirect(url_for("homepage"))
            except:
                return render_template("login.html" , error="Login Failed")
    return render_template("login.html" , error="")

@app.route('/signup' , methods=['GET' , 'POST'])
def signup():

    if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            try:
                login_session['user'] = auth.create_user_with_email_and_password(email, password)
                userid = login_session['user']['localId']
                user = {
                    "email": email,
                    "username": request.form['username']
                }
                db.child("Users").child(userid).set(user)
                uname = db.child("Users").child(login_session['user']['localId']).get().val()
                login_session['uname'] = uname['username']
                return redirect(url_for("homepage"))
            except:
                return render_template("signup.html" , error="There has Been an Error, please try again")

    return render_template("signup.html" , error="")

@app.route('/famousSimilarity' , methods=['GET' , 'POST'])
def upload():
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                return render_template("famous.html", error=True)
            file = request.files['file']
            if file.filename == '':
                return render_template("famous.html", error=True)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                result = backend.apiQuery('static/Upload_Folder/' + filename)
                path = 'Upload_Folder/' + filename
                data = {
                    "imgpath" : {"image1" : path},
                    "score" : result
                }
                db.child("Users").child(login_session['user']['localId']).child("Media").push(data)
                print([path])
                return render_template("analysis.html" , result=result , photos=[path] , uname=login_session['uname'])
        except:
            return render_template("famous.html" , error=True)
    return render_template("famous.html" , error=False)


@app.route('/photoCompare' , methods=['GET' , 'POST'])
def comapre():
    if request.method == 'POST':
        # try:
            if 'file' not in request.files or 'file1' not in request.files:

                return render_template('similarity.html' , error='File not Found')
            file = request.files['file']
            file1 = request.files['file1']
            if file.filename == '' or file1.filename == '':
                return render_template('similarity.html' , error='File Does not Exist')
            if file and allowed_file(file.filename):
                if file1 and allowed_file(file1.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    filename1 = secure_filename(file1.filename)
                    file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
                    path1 = 'static/Upload_Folder/' + filename
                    path2 = 'static/Upload_Folder/' + filename1
                    result = backend.compare_two_images(path1, path2)
                    path1 = 'Upload_Folder/' + filename
                    path2 = 'Upload_Folder/' + filename1
                    print("ok")
                    data = {
                        "imgpath": {"image1": path1 , "image2" : path2},
                        "score": result
                    }
                    db.child("Users").child(login_session['user']['localId']).child("Media").push(data)
                    return render_template('analysis.html' , result=result , photos=[path1 , path2] , uname=login_session['uname'])
        # except:
        #     return render_template('similarity.html', error='Upload Falied')
    return render_template('similarity.html' , error="")

@app.route('/similaritys/<string:user>' , methods=['GET' , 'POST'])
def similarity(user):
    if user == login_session['uname']:
        data = db.child("Users").child(login_session['user']['localId']).child("Media").get().val()
        return render_template("view.html" , error=False , data=data)
    else:
        return render_template("view.html" , error=True , data=[])



#Code goes above here

if __name__ == '__main__':
    app.run(debug=True)