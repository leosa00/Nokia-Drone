#The following code, creates an element by calling a POST request to the attestation server. The element is created according to the json file, elementJson.json

import requests
import json
import re
import os
import subprocess
#extracts the AK from the device, by using specific tpm2 tools and by utilizing tpm2_send over ssh. Takes the device ip address as the input

def akExtract(user):
    ak = f"tpm2_readpublic -c 0x810100AA -o /tmp/ak -fpem --tcti='cmd:ssh {user} tpm2_send'"
    
    # Execute the command and capture the output
    outputAk = os.popen(ak).read()
    # Save the command output to the specified file
    with open("ak.txt", "w") as file:
        file.write(outputAk)
    
    # Save the contents of the /tmp/k file
    os.system("cat /tmp/ak >> ak.txt")

#extracts the EK from the device, by using specific tpm2 tools and by utilizing tpm2_send over ssh. Takes the device ip address as the input

def ekExtract(user):
    ek = f"tpm2_readpublic -c 0x810100EE -o /tmp/ek -fpem --tcti='cmd:ssh {user} tpm2_send'"

    outputEk = os.popen(ek).read()
    # Save the command output to the specified file
    with open("ek.txt", "w") as file:
        file.write(outputEk)
    
    # Save the contents of the /tmp/k file
    os.system("cat /tmp/ek >> ek.txt")

#extracts the name and public key from Ek and AK files
def extract_name_and_public_key(file_path):
    hand=""
    
    if(file_path == "ak.txt"):
        hand = "0x810100AA"
    else:
        hand = "0x810100EE"

    with open(file_path, "r") as file:
        file_content = file.read()

    name_match = re.search(r"name: (\w+)", file_content)
    public_key_match = re.search(r"(-----BEGIN PUBLIC KEY-----.*?-----END PUBLIC KEY-----)", file_content, re.DOTALL)

    name = name_match.group(1) if name_match else None
    public_key = public_key_match.group(1).replace("\n", "") if public_key_match else None
    result = {"public":public_key,"handle":hand, "name":name}

    return result


#returns a format with all the variables required for the json file
def createJson(name,desc,endpoint,tag,ek,ak):
    dictionary = {
     "name":name,
     "description":desc,
     "endpoint": endpoint,
     "protocol":"A10HTTPRESTv2",
     "tags":["pi","tpm2",tag],
     "sshkey":{"key":"","timeout":0,"username":""
     },
     "tpm2":{"device":"/dev/tpmrm0","ekcerthandle":"0x1c0002","ek":ek,
     "ak":ak
     },
     "uefi":{"eventlog":""
     },
     "ima":{"asciilog":""
     },
     "txt":{"log":""
     },
    }
    return dictionary

#Creates an element by sending a post request to end point /elements
def sendRequest(name,desc,endpoint,tag,ek,ak):
    # Serializing json
    json_object = createJson(name,desc,endpoint,tag,ek,ak)
    

    r = requests.post('http://194.157.71.11:8520/element', json=json_object)

    print(r.ok)
    
    