from instaloader import Instaloader, Profile
from firebase_helpers import randomAccount

L = Instaloader()

def randomLogin():
    random_account = randomAccount()
    L.login(random_account['username'], random_account['password'])

def storiesFrom(profileID):
    return L.get_stories(userids=[int(profileID)])

def usernameCheck(username):
    try:
        Profile.from_username(L.context, username)
    except:
        return False
    else:
        return True
    
def profileData(username):
    LA = Instaloader()
    profile = Profile.from_username(L.context, username)
    LA.close()
    return profile