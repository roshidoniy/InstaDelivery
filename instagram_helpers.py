import time
from instaloader import Instaloader, Profile, RateController
from firebase_helpers import randomAccount
from instaloader.exceptions import ProfileNotExistsException
L = Instaloader()

def randomLogin():
    L.close()
    random_account = randomAccount()
    L.login(random_account['username'], random_account['password'])
    print(random_account)

# def storiesFrom(profileID):
#     return L.get_stories(userids=[int(profileID)])
    
def usernameCheck(username):
    try:
        Profile.from_username(L.context, username)
    except:
        return False
    else:
        return True
    

def profileData(username):
    if(L.context.is_logged_in):
        pass
    else:
        randomAccount()
    profile = Profile.from_username(L.context, username)
    return profile