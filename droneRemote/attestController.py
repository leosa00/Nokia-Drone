import requests
import json


#returns a format with all the variables required for the json file
def createJson(elementId,policId,sessionId,params):
    dictionary = {
    "eid":elementId,
    "pid":policId,
    "sid":sessionId,
    "parameters":params
    }
    return dictionary

#sends the created json file to end point attest, returns the attest claim id. This is used in the createExpected.py to automatically attest a device for 
#the creation of an expected value

def sendRequest(elementId,policId,sessionId,params):
   
    json_object = createJson(elementId,policId,sessionId,params)
    
    try:
        r = requests.post('http://194.157.71.11:8520/attest', json=json_object)
    except:
        raise Exception("request to attest was not successfull")
        
    itemId = r.json()
    print(itemId['itemid'])
    return (itemId['itemid'])
