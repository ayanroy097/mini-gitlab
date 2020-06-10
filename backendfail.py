# from flask import Flask, request, redirect, session, url_for, render_template
from flask import *
import requests
from requests.auth import HTTPBasicAuth
from flask_session import Session
import sys
import os
from requests_oauthlib import OAuth2Session
from flask.json import jsonify
import json
# from flask.json import jsonify
# import time
# file=sys.stderr


app = Flask(__name__)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"
app.secret_key = "xyz"

base_url = "https://api.github.com/user"
repo_url = "https://api.github.com/repos"


client_id = "b93f1eb7c843f0b5eae8"
client_secret = "e32c4a8fca0a4f5dc6cf23082354c9777f679981"
authorization_base_url = 'https://github.com/login/oauth/authorize'
token_url = 'https://github.com/login/oauth/access_token'


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/authorize")
def authorizeGit():
    github = OAuth2Session(client_id)
    authorization_url, state = github.authorization_url(authorization_base_url)

    session['oauth_state'] = state
    print(state, file=sys.stderr)
    return redirect(authorization_url)


@app.route("/callback/", methods=["GET"])
def callback():
    state = request.args.get('state')
    github = OAuth2Session(client_id, state=state)
    token = github.fetch_token(token_url, client_secret=client_secret, authorization_response=request.url)
    
    session['oauth_token'] = token

    return redirect(url_for('makeChanges', token=token))


@app.route("/makeChanges/", methods=["GET", "PATCH"])
def makeChanges():
    
    token = request.args.get('token')
    # token = session['oauth_token']
    github = OAuth2Session(client_id, token=token)
    if request.method == "PATCH":
        # state = request.args.get('state')
        
        user = session['user']
        
        # github = OAuth2Session(client_id, token=token)
        reponame = session['reponame']
        name = request.form.get('name')
        desc = request.form.get('desc')
        priv = request.form.get('Private')
        url = "https://api.github.com/repos/" + user + "/" + reponame
        payload = {"name": name,
                   "description": desc,
                   "private": priv,                  
                   }
        r = github.patch(url, data=payload)

    # session['github'] = github.jsonify()
    return render_template("makeChanges.html")





@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        response = requests.get(base_url, auth=HTTPBasicAuth(username, password))
        source = response.json()
        session['user'] = username
        session['pass'] = password

        if username in source.get('login'):
            # ,username = username,password=password
            return redirect(url_for("profile"))
            # return render_template("profile.html",data =source,profile = user_info, repos = repos)
        else:
            return render_template("home.html", error="User not found...")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/repository/", methods=['GET'])
def repoDIsplay():
    reponame = request.args.get('reponame')
    username = session['user']
    session['reponame'] = reponame
    password = session['pass']
    repoResponse = requests.get(
        repo_url + "/"+username+"/"+reponame, auth=HTTPBasicAuth(username, password))
    contentResponse = requests.get(
        repo_url + "/"+username+"/"+reponame+"/contents", auth=HTTPBasicAuth(username, password))
    repoInfo = repoResponse.json()
    contentInfo = contentResponse.json()
    return render_template('repository.html', reponame=reponame, repoInfo=repoInfo, contentInfo=contentInfo)


@app.route('/profile/', methods=['GET'])
def profile():
    # username = request.args.get('username')
    # password = request.args.get('password')
    username = session['user']
    password = session['pass']
    response_user = requests.get(
        base_url, auth=HTTPBasicAuth(username, password))
    response_repos = requests.get(
        base_url + "/repos", auth=HTTPBasicAuth(username, password))

    user_info = response_user.json()
    repos = response_repos.json()
    return render_template('profile.html', profile=user_info, repos=repos, username=username)
# @app.route('/profile/',methods=['GET'])
# def profile():
#     username = request.args.get('username')
#     response_user = requests.get(base_url + username)
#     response_repos = requests.get(base_url + username + "/repos")

#     user_info = response_user.json()
#     repos = response_repos.json()
#     return render_template('profile.html',profile = user_info, repos = repos, username = username )
    # print(type(data), file=sys.stderr)
    # print(type(user_info), file=sys.stderr)
    # print(type(repos), file=sys.stderr)
    # print(type(username), file=sys.stderr)

    # return render_template('profile.html',data =session["gitObject"],profile = session["user_info"], repos = session["repoObject"], username = session["username"] )
    # if :
    # else:
    #     return '<p>Please login first</p>'


app.run(debug=True)
# if __name__ == "__main__":
# This allows us to use a plain HTTP callback

# app.secret_key = os.urandom(24)
