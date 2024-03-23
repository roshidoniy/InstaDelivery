from datetime import datetime
from firebase_admin import firestore, credentials, initialize_app

cred = credentials.Certificate("./instadeliver0SDK.json")
initialize_app(cred)

db = firestore.client()
col_ref = db.collection('users_info')

def followingList(userID): 
    return col_ref.document(f"{userID}").get().to_dict()['follows']


def addFollowing(userID, followTo):
    doc_ref = col_ref.document(f"{userID}")
    followsArray = list(doc_ref.get().to_dict()['follows'])
    
    if len(followingList(userID)) == 3:
        print("Nope")
        return False
    else:
        # adds new follow to follows property in the document
        doc_ref.update({
        'follows': [followTo] + followsArray
        })

        return True

def isUserExist(telegramID) -> bool:
    doc_ref = col_ref.document(f"{telegramID}")

    return doc_ref.get().exists

def setupAccount(userID, fullName):

    currentTime = datetime.now().strftime("%H:%M")
    
    data = {
        'id': userID,
        'fullname': fullName,
        'fetchTime': currentTime,
        'follows': [],
        'last_post_time': currentTime,
    }
    
    doc_ref = col_ref.document(f"{userID}")
    doc_ref.set(data)
