import database as data
import sessionController as session
import elementController as el
import expectedValueController as e
import attestController as att
import expectedValueController as ex
import attestVerifyController as ver

def findDroneByID(droneID):
    for x in data.droneTelemetry:
            if (x['droneID'] == droneID):
                return x, True
    return "could not find drone",False


def createAttElement(ipaddr,device, name, description, tag):
    el.ekExtract(device)
    el.akExtract(device)
    ipaddr = device.split("@",1)[1]
    akInfo = "ak.txt"
    ekInfo = "ek.txt"
    ak= el.extract_name_and_public_key(akInfo)
    ek= el.extract_name_and_public_key(ekInfo)
    el.sendRequest(name,description,f"http://{ipaddr}:8530",tag,ek,ak)

def attest(element, policies, session):
    elementId = e.element_id_finder(element)
    claimIds = []
    for x in policies:
        policyId = e.policy_id_finder(x)
        claim = att.sendRequest(elementId, policyId, session, {
        "param1": "value1",
        "param2": "",
        "param3": ""
        })
        claimIds.append(claim)
    return claimIds

def createExpectedValue(element, policies, claims):
    elementId = ex.element_id_finder(element)

    for x,y in zip(policies,claims):
        policyId = ex.policy_id_finder(x)
        intent = ex.check_policy_intent(policyId)

        if (intent != "tpm2/quote"):
            raise Exception(f"policy {x} cannot be used to create an expected value, needs to have tpm2/quote intent") 


        pcrdigest,firmwareVersion = ex.getEVs(y)
        evs = {
        "attestedValue":pcrdigest,
        "firmwareVersion":str(firmwareVersion)
        }   

        ex.sendRequest(f'drone {element} expected value',f'policy {x}',elementId,policyId,evs)
    
    return True

def verify(rules,session,claims):
    ruleFailes = []

    for x in claims:

        for y in rules:
            result = ver.sendRequest(x,session, y)

            if not (result == 0):
                ruleFailes.append(f'rule {y} failed')

    return ruleFailes

def addDrone(d):
   
    errors =[]
    for x in data.drone:
        
        if(d['droneID'] == x['droneID']):
            errors.append("drone Id already exists")
        
    if not(('name' in d)):
        errors.append("name field is missing")

    if not(('description' in d)):
        errors.append("description field is missing")

    if not(('address' in d)):
        errors.append("address field is missing")

    if not(('tpm2' in d)):
        errors.append("tpm2 field is missing")

    if (len(errors) > 0):
        return (errors, 'error')
    else:
        data.drone.append(d)
        
    tpmData = d['tpm2']
    try:
        sesh = session.makeSession('194.157.71.11:8520',f'session for drone {d["droneID"]}')
        createAttElement('194.157.71.11:8520',tpmData['device'],d['droneID'],d['description'],tpmData['tag'])
        
        policies = ["Pi Fakeboot CRTM","Pi Fakeboot SRTM"]

        claimIds = attest(d['droneID'],policies,sesh)

        createExpectedValue(d['droneID'],policies,claimIds)

        session.closeSession('194.157.71.11:8520',sesh)
    except:
        raise errors.append("failed to create element/excpected values")
    
    return (errors,d)

def receiveTelemetry(d):  
    errors= []
    verificationFails= []
    if not(('droneID' in d)):
        errors.append("droneID is missing")

    if not(('longitude' in d)):
        errors.append("longitude is missing")

    if not(('latitude' in d)):
        errors.append("latitude is missing")
    
    if not(('altitude' in d)):
        errors.append("altitude is missing")
    
    if (len(errors) > 0):
        return (errors, 'error')
    else:
        found_matching_drone = False

        for index, x in enumerate(data.droneTelemetry):
            if (x['droneID'] == d['droneID'] or x['droneID'] == ""):
                data.droneTelemetry[index] = d  
                found_matching_drone = True
                break  

        if not found_matching_drone:
            data.droneTelemetry.append(d)
        
        try:
            sesh = session.makeSession('194.157.71.11:8520',f'session for drone {d["droneID"]}')

            policies = ["Pi Fakeboot CRTM","Pi Fakeboot SRTM"]

            rules = ["tpm2_attestedValue","tpm2_firmware","tpm2_magicNumber","tpm2_safe"]

            claimIds = attest(d['droneID'],policies,sesh)
        
            verificationFails = verify(rules,sesh,claimIds)
            errors.append(verificationFails)
            session.closeSession('194.157.71.11:8520',sesh)

        except:
            errors.append("failed to verify")
            return errors, d
   
    return errors, d
    
