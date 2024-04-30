from datetime import datetime
from firebase_admin import firestore, credentials, initialize_app
import random

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
    # currentTime = datetime.now()
    # utc time 
    # fetchTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    data = {
        'id': userID,
        'fullname': fullName,
        # 'fetchTime': fetchTime,
        'follows': [],
        # 'last_post_time': currentTime,
    }
    
    doc_ref = col_ref.document(f"{userID}")
    doc_ref.set(data)

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

def randomAccount():
    col_ref_accounts = db.collection('instaAccounts').list_documents()

    doc_ids = [doc.id for doc in col_ref_accounts]

    if not doc_ids:
        return None

    # Choose a random document ID
    random_doc_id = random.choice(doc_ids)

    # Retrieve the random document
    random_doc_ref = db.collection("instaAccounts").document(random_doc_id)
    random_doc = random_doc_ref.get()

    if random_doc.exists:
        return random_doc.to_dict()
    else:
        return None
    # get random account from the collection
