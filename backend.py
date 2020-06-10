from flask import *
import requests
from requests.auth import HTTPBasicAuth
# from flask_session import Session
import sys
import os
# from requests_oauthlib import OAuth2Session
from flask.json import jsonify
import json
import requests

gh = Flask(__name__)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"
gh.config['SECRET_KEY'] = "thisisasecret"

base_url = "https://api.github.com/user"
repo_url = "https://api.github.com/repos"


# client_id = "fb34925501b252703f43"
# client_secret = "2d2c634b0960b3a645fdb0f00066e5846764929a"
# authorization_base_url = 'https://github.com/login/oauth/authorize'
# token_url = 'https://github.com/login/oauth/access_token'


@gh.route("/")
def home():
    return render_template("home.html")


# @gh.route("/authorize")
# def authorizeGit():
#     github = OAuth2Session(client_id)
#     authorization_url, state = github.authorization_url(authorization_base_url)

#     session['oauth_state'] = state
#     print(state, file=sys.stderr)
#     return redirect(authorization_url)


# @gh.route("/callback", methods=["GET"])
# def callback():
#     # state = request.args.get('state')
#     github = OAuth2Session(client_id, state=session.get('oauth_state'))
#     token = github.fetch_token(
#         token_url, client_secret=client_secret, authorization_response=request.url)

#     session['oauth_token'] = token

#     return redirect(url_for('makeChanges'))


# @gh.route("/makeChanges/", methods=["GET", "PATCH"])
# def makeChanges():

#     token = session.get('oauth_token')
#     # token = session['oauth_token']
#     github = OAuth2Session(client_id, token=token)
#     if request.method == "PATCH":
#         # state = request.args.get('state')

#         user = session['user']

#         # github = OAuth2Session(client_id, token=token)
#         reponame = session['reponame']
#         name = request.form.get('name')
#         desc = request.form.get('desc')
#         priv = request.form.get('Private')
#         url = "https://api.github.com/repos/" + user + "/" + reponame
#         payload = {"name": name,
#                    "description": desc,
#                    "private": priv,
#                    }
#         r = github.patch(url, data=payload)
#         return jsonify(github.get('https://api.github.com/user').json())
#     # session['github'] = github.jsonify()
#     return render_template("makeChanges.html")


@gh.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        response = requests.get(
            base_url, auth=HTTPBasicAuth(username, password))
        source = response.json()
        session['user'] = username
        session['pass'] = password

        if username in source.get('login'):
            return redirect(url_for("profile"))

        else:
            return render_template("home.html", error="User not found...")

    return render_template("login.html")


@gh.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@gh.route("/repository/", methods=['GET'])
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


@gh.route("/delete", methods=["GET", 'DELETE'])
def delete():
    user = session['user']
    reponame = session['reponame']
    password = session['pass']
    url = "https://api.github.com/repos/"+user+"/"+reponame
    x = requests.delete(url, auth=HTTPBasicAuth(user, password))
    return '<p>Repository Deleted.Check Profile</p>'


@gh.route("/update", methods=["GET", "POST","PATCH"])
def update():

    user = session['user']
    reponame = session['reponame']
    password = session['pass']
    name = request.form.get('name')
    desc = request.form.get('desc')
    priv = request.form.get('Private')
    payload = {
        "name": name,
        "description": desc,
        "homepage": "https://github.com",
        "private": priv,
        "has_issues": True,
        "has_projects": True,
        "has_wiki": True
        }
    url = "https://api.github.com/repos/"+user+"/"+reponame
    x = requests.patch(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload))
    return '<p>Repository Updated.Check Profile</p>'

@gh.route("/create", methods=["GET", "POST"])
def create():

    user = session['user']
    # reponame = session['reponame']
    password = session['pass']
    name = request.form.get('name')
    desc = request.form.get('desc')
    priv = request.form.get('Private')
    payload = {
        "name": name,
        "description": desc,
        "homepage": "https://github.com",
        "private": priv,
        "has_issues": True,
        "has_projects": True,
        "has_wiki": True
        }
    url = "https://api.github.com/user/repos"
    x = requests.post(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload))
    return '<p>Repository Created.Check Profile</p>'


@gh.route('/profile/', methods=['GET'])
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


if __name__ == "__main__":
    gh.run(debug=True)
