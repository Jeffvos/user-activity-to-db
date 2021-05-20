import urllib2
import sys
import base64
import json
import urllib

from clients import psql as DB
from config import config
config = config()
DB = DB.Client()

class GetUsers:
    def __init__(self):
        self.url = config['jira']['userexp_url']
        user = config['jira']['basic_auth']['username']
        passw = config['jira']['basic_auth']['password']
        auth_user = user + ":" + passw
        basicauth = "Basic " + base64.b64encode(b"{}:{}".format(user, passw))
        self.headers  ={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": basicauth}
        self.json_file = "jira-users.json"
        self._return_json = {}
            
    def user_to_json(self, activeUsers, inactiveUsers):
        data = urllib.urlencode({
            "userexport_searchstring":"",
            "userexport_activeUsers":activeUsers,
            "userexport_inactiveUsers":inactiveUsers
            })
        try:
            request = urllib2.Request(url=self.url, data=data, headers=self.headers)
            request.get_method = lambda: "POST"
            contents = urllib2.urlopen(request).read()
            assert contents
            self._return_json = contents
            self.normalize_json(activeUsers, inactiveUsers)

        except urllib2.HTTPError as e:
            print ("HTTP error: " + str(e.code))
            print ("Exiting...")
            sys.exit(1)

    def normalize_json(self, activeUsers, inactiveUsers):
        loaded = json.loads(self._return_json)
        users = loaded['jiraUserObjects']
        if activeUsers == 'true':
            print('Checking active users')
            for user in users:
                DB.insert_new(user)
        else:
            print('Checking deactivated users')
            for user in users:
                DB.check_inactive_user(user)    
        
if __name__ == "__main__":
    instance = GetUsers()
    instance.user_to_json("false","true")
    instance.user_to_json("true","false")