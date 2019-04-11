# ConfigChecker
Tool to detect configuration changes in storage arrays (Ex: DellEMC Unity, VMAX ...)

# Summary
- It is written in Python and leverages the DeepDiff library to compare the JSON files
- It compares the output of the specified REST API calls against an archived well-known copy of the same calls to see if any changes have occurred
- We are showing how it works with DellEMC Unity but it will work with anything that returns JSON

# Sample Workflows
Firstly add the credentials to the environment so that the script can read it. Using environment vars will help us deploy in Cloud Foundry later. For example in Windows you can use the set command:

```
set username = admin
set password = mypassword
```
Then jump in to Python (I am using 2.7.12) and import json and configchecker

```python
import json
from configchecker import *
```
Create a Gold config for an array. We are passing its IP address here, instead of name. You can check that the JSON file has been created
```python
save_config('10.1.1.1')
```
Then introduce some changes in the array using the Unisphere interface and then check that the script can detect the changes
```python
result = compare_config(load_config('10.1.1.1'),build_config('10.1.1.1', 'unity'))
print result
```
```
{
  "iterable_item_removed": {
    "root['lun'][11]": {
      "content": {
        "sizeTotal": 21474864800,
        "health": {
          "descriptionIds": [
            "ALRT_VOL_OK"
          ],
          "descriptions": [
            "The LUN is operating normally. No action is required."
          ],
          "value": 5
        },
        "id": "sv_200",
        "name": "testing-API"
      }
    }
  },
  "iterable_item_added": {
    "root['lun'][1]": {
      "content": {
        "sizeTotal": 133143986176,
        "health": {
          "descriptionIds": [
            "ALRT_VOL_OK"
          ],
          "descriptions": [
            "The LUN is operating normally. No action is required."
          ],
          "value": 5
        },
        "id": "sv_103",
        "name": "UnityDS"
      }
    }
  }
}
```

# About DellEMC Unity REST API
Unity is a unified storage which provides block and file capabilities in a single array. Unity features a comprehensive API which exposes a vast amount of configuration settings and allows the authenticated user to perform all the typical management actions one can think off: LUNs, File Systems, etc. The DellEMC Unity is a great tool for customers to automate storage array operations in order to achieve cloud-like operations on-prem

Some things to bear in mind when working with the DellEMC Unity API:
 - It uses HTTPS. Authentication is HTTP Basic
 - Authentication is required for all API calls except for the "GET /api/instances/basicSystemInfo/0" endpoint which provides basic information such as array model and name
 - You can query full collections "GET /api/types/<collection_name>/instances", ex: https://1.1.1.1/api/types/lun/instances
 - Or individual instances "GET /api/instances/disk/<id>"
 - It requires the following 3 headers
 ```
 {
  'Accept':'application/json',
  'Content-type':'application/json',
  'X-EMC-REST-CLIENT':'true'
 }
 ```
 - In order to simplify the output and get faster responses:
   - You need to explicitly specify what fields you want to retrieve. When no fields are specified the API will return only the "Id" of each instance. To understand the reason why it's been implemented this way think of this: the disk endpoint contains 33 fields and the Unity 600 can have up to 1000 disks !!!
   - It implements a very handy SQL-like query to filter the output of a collection including filtering, sorting and aggregating

For more details check out the Unity official documents:
 - DellEMC Unity [REST API Programmer's Guide](https://www.emc.com/collateral/TechnicalDocument/docu69331.pdf)
 - DellEMC Unity [REST API Reference Guide](https://uk.emc.com/collateral/TechnicalDocument/docu91031.pdf)

# To Do
 - Open up the tool to be used with other arrays/appliances. Separate the Unity specific pieces away into its own library and adapt the main script to make it easy to integrate other API's
 - Rest API interface that exposes the main functions such as "create new Gold copy" and "compare current config against the archive Gold copy"
 - Given that we are dealing with JSON files it would make sense to do away with text files and use MongoDB at the backend
 - Store more point-in-time array configurations and provide a historical record of configurations that can be queried

