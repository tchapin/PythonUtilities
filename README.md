# PythonUtilities  
These utilities require a config.json file to store and retrieve sensitive data like usernames and passwords. This file is not included in this repo.  
Example:  
```
{
    "username": "ted.chapin",
    "password": "passw0rd"
}
```  
Wherever you see `CONFIG.get("key", "")`, make sure that key exists in the config.json file.  
