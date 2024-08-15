from instaloader import Instaloader, Profile, Story
from firebase_helpers import randomAccount
L = Instaloader()

def randomLogin():
    random_account = randomAccount()
    L.login(random_account['username'], random_account['password'])
def allStories(profileID):
    return L.get_stories(userids=[int(profileID)])

def usernameCheck(username):
    # Anonymus Session
    # print(L.context.  )

    LA = Instaloader()

    try:
        Profile.from_username(LA.context, username)
    except:
        return False
    else:
        return True
    
    
def profileData(username):
    LA = Instaloader()
    profile = Profile.from_username(LA.context, username)
    LA.close()
    return profile