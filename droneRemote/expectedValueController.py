import requests
import json
import re
#check to see if a an expected value already exists for the same element and policy
def check_expected(policyId, elementId):
    r = requests.get(f'http://194.157.71.11:8520/expectedValue/{elementId}/{policyId}')
    if(r.ok):
        j = json.loads(r.text)
        print("JSON=",j["itemid"])
        return r.ok,j["itemid"]
    else:
        return r.ok, ""

#Finds policy id from policy name as input
def policy_id_finder(policy):
    #get all policies
    r = requests.get('http://194.157.71.11:8520/policies')
    policies = r.json()
    size = policies['length']
    
    #check which policy id matches the name given
    for x in range (0,size):
        element = policies['policies'][x]
        r1 = requests.get('http://194.157.71.11:8520/policy/{0}'.format(element))
        availablePolicies = r1.json()
        
        if(availablePolicies['name'].lower() == policy.lower()):
            return(availablePolicies['itemid'])
    
    raise Exception(f"No such policy exists, please check the name")

#checks if the policy intent is tpm2/quote as these require and expected value
def check_policy_intent(policyId):
    r = requests.get(f'http://194.157.71.11:8520/policy/{policyId}')
    intent = r.json()['intent']
    return intent
    

#Finds element id from element name as input
def element_id_finder(element):
    #get all elements
    r = requests.get('http://194.157.71.11:8520/elements')
    elements = r.json()
    size = elements['length']
    
    #check which element id matches the name given
    for x in range (0,size):
        el = elements['elements'][x]
        r1 = requests.get('http://194.157.71.11:8520/element/{0}'.format(el))
        specificElement = r1.json()
        
        if(specificElement['name'].lower() == element.lower()):
            return(specificElement['itemid'])
    
    raise Exception(f"No such element exists, please check the name")

#returns a format with all the variables required for the json file
def createEVstructure(name,desc,element,policy,evs):
    dictionary = {
    "description": desc,
    "name": name,
    "elementid": element,
    "policyid": policy,
    "evs": evs
    }
    return dictionary

#returns the values for the pcrdigest and firmwareVersion of the corresponding attestClaim. Takes in the attest claim id as an input.
def getEVs(attestClaimId):
    r = requests.get('http://194.157.71.11:8520/claim/{0}'.format(attestClaimId))
    info = r.json()['body']
    pcrdigest= info['AttestedQuoteInfo']['PCRDigest']
    firmwareVersion= info['FirmwareVersion']

    return pcrdigest,firmwareVersion

#Creates an expected value by posting the required json file to endpoint /expectedValue
def sendRequest(name,desc,elementId,policyId,evs):
    # Serializing json
    evstr = createEVstructure(name,desc,elementId,policyId,evs)

    expected = check_expected(policyId,elementId)


    if(expected[0]):
        # add itemid to json object
        evstr["itemid"] = expected[1]
        r = requests.put('http://194.157.71.11:8520/expectedValue', json=evstr)
        print("Expected value has been updated")
    else:
        r = requests.post('http://194.157.71.11:8520/expectedValue', json=evstr)
        print("New expected value has been created")

    print(r.text)
    
