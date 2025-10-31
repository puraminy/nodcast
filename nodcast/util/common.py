appname = "nodcast"
appauthor = "App"
user = 'na'
profile = "default"

def set_app(name,author="App",_user="na",_profile="default"):
    global appname, appauthor, user, profile
    appname = name
    appauthor = author
    user = _user
    profile = _profile

