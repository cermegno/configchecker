import os
import json
from deepdiff import DeepDiff
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#pass this as a parameter
#target = "10.1.1.1"
#read these from the environment
#username = "admin"
#password = "mypassword"

unity_headers = {  'Accept':'application/json',
                   'Content-type':'application/json',
                   'X-EMC-REST-CLIENT':'true'}

#Sample endpoints for Unity (LUNs, File Systems and ports)
unity_endpoints = {
    "lun" : "/api/types/lun/instances?fields=id,name,health,sizeTotal&compact=true",
    "filesystem" : "/api/types/filesystem/instances?fields=id,name,health,sizeTotal&compact=true",
    "fcPort" : "/api/types/fcPort/instances?fields=id,slotNumber,health,currentSpeed&compact=true"
    }

session = requests.Session()

def read_creds():
    """Reads credentials from environment variables"""
    if not username:
        username = os.environ['ccuser']
        global username
    if not password:
        password = os.environ['ccpass']
        global password
    return

def load_config(array_name):
    """looks for an array_name.json file and returns it in dict format"""
    file_path = array_name + ".json"
    f = open(file_path,'r')
    config = json.load(f)
    f.close()
    return config

def save_config(array_name, config=None):
    """creates a Gold config file for a given array name or IP. Optionally pass a config dict"""
    if not config:
        config = build_config(target, 'unity')
    c = json.dumps(config, indent = 2)
    file_path = array_name + ".json"
    f = open(file_path,'w')
    f.writelines(c.splitlines(True))
    f.close()

    return

def build_config(array_name, array_type):
    """builds a single complete json config for array_name with all calls defined for its array_type"""
    read_creds()
    config = {}
    
    # determine what endpoints to use depending on the array type
    #if array_type == 'unity': ...
        
    for endpoint in unity_endpoints:
        url = "https://" + target + unity_endpoints[endpoint]
        response = session.get(url, headers=unity_headers, auth=(username, password), verify=False)
        r = json.loads(response.content)
        config[endpoint] = r['entries']

    return config

def compare_config(gold, new):
    """compares two json configs and returns a dict with the differences"""
    diff = DeepDiff(gold, new, ignore_order=True)
    result = json.dumps(diff, indent=2)
    return result

#////////// SAMPLE WORKFLOWS //////////#
### Create a new config by calling the API
##config = build_config(target, 'unity')

### Create Gold config JSON file
##save_config(target)

### Load JSON file
##print json.dumps(load_config(target), indent = 2)

### Get a new config via the API and compare it with the Gold config
##result = compare_config(load_config(target),build_config(target, 'unity'))
##print result
