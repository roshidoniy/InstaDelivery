from datetime import datetime
from firebase_admin import firestore, credentials, initialize_app

cred = credentials.Certificate("./instadeliver0SDK.json")
initialize_app(cred)

db = firestore.client()
col_ref = db.collection('users_info')

def followingList(userID): 
    return col_ref.document(f"{userID}").get().to_dict()['follows']

def unFollow(userID, toRemove):
    doc_ref = col_ref.document(f"{userID}")
    doc_ref.update({
        'follows': firestore.firestore.ArrayRemove([toRemove])
    })

def addFollowing(userID, followTo):
    doc_ref = col_ref.document(f"{userID}")
    followsArray = list(doc_ref.get().to_dict()['follows'])
    
    # adds new follow to follows property in the document
    doc_ref.update({
    'follows': [followTo] + followsArray
    })



def isUserExist(telegramID) -> bool:
    doc_ref = col_ref.document(f"{telegramID}")

    return doc_ref.get().exists

def setupAccount(userID, fullName):

    currentTime = datetime.now()
    fetchHour = datetime.now().strftime("%H")
    fetchMinute = datetime.now().strftime("%M")
    fetchSecond = datetime.now().strftime("%S")
    print(currentTime)
    
    data = {
        'id': userID,
        'fullname': fullName,
        'fetchHour': fetchHour,
        'fetchTime': {
            'hour': int(fetchHour),
            'minute': int(fetchMinute),
            'second': int(fetchSecond)
        },
        'follows': [],
        'last_post_time': str(currentTime),
    }
    
    doc_ref = col_ref.document(f"{userID}")
    doc_ref.set(data)

def getTime(telegramID):
    doc_ref = col_ref.document(f"{telegramID}")
    
    return doc_ref.get().to_dict()['last_post_time']
    # fetchHour = doc_ref.get().to_dict()['fetchHour']
    # fetchMinute = doc_ref.get().to_dict()['fetchMinute']

    # return [fetchHour, fetchMinute]

def setting(time, telegramID):
    doc_ref = col_ref.document(f"{telegramID}")

    newTime = time.split(":", 2)

    print(newTime)

    doc_ref.update({
        'fetchTime': {
            'hour': newTime[0],
            'minute': newTime[1]
        }
    })