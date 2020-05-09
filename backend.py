from flask import *
import requests
from requests.auth import HTTPBasicAuth


app = Flask(__name__)  
app.secret_key = "abc"  
base_url = "https://api.github.com/users/" 

@app.route("/")
def home():
    return render_template("home.html")
 
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        response = requests.get('https://api.github.com/user', auth=(username ,password))
        source = response.json()
        
        response_user = requests.get(base_url + username)
        response_repos = requests.get(base_url + username + "/repos")

        user_info = response_user.json()
        repos = response_repos.json()

        if username in source.get('login') :
            session["username"] = username
            session["gitObject"] = source
            # return redirect(url_for("profile",data =source,repos = repos,profile = user_info))
            return render_template("profile.html",data =source,profile = user_info, repos = repos)
        else:
            return render_template("home.html",error = "User not found...")
            
    return render_template("login.html")  
 

 
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home")) 
 
@app.route('/profile')  
def profile():  
    if 'username' in session:  
        username = session['username'] 
        job = session["gitObject"] 
        return render_template('profile.html',name=username, gob = job)  
    else:  
        return '<p>Please login first</p>'  
  
if __name__ == '__main__':  
    app.run(debug = True)  