import requests

#Creates a session and return the session id
def makeSession(ipaddr, message):
    try:
        r = requests.post(f'http://{ipaddr}/session', json={"message":message})
        session = r.json()
        print(session['itemid'])
        return session['itemid']
    except:
        raise Exception("something went wrong with session creation")

#closes a session by sessionId
def closeSession(ipaddr, sessionId):
    try:
        r = requests.delete(f'http://{ipaddr}/session/{sessionId}')
        print(r.ok)
    except:
        raise Exception("could not delete session")