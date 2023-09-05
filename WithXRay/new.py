import requests
import json
from requests.auth import HTTPBasicAuth
import codecs
import binascii

# def CommentWriter():
def CommentWriter(test_id_input, comment_input):
  comment = []
  URL = f'https://jira.lar.tech/rest/raven/1.0/api/testrun/{103}/comment'
  r2 = requests.get(URL, auth=('e.khasanov', 'MyKhasanovy1991!'),headers={'X-Atlassian-Token': 'MTA0NDc2OTk3NjkzOolnsvIoPFJQcs5EMXmjj6Qos7pR'}, verify=False)
  r2 = r2.content
  d = json.loads(r2)
  d = d['raw']
  comment.append(d)
  comment.append('new comment 4')
  comment = str(comment).replace('[','').replace(']','').replace('\\','').replace('"','').replace("'",'')
  comment = str(comment)
  r2 = requests.put(URL, auth=('e.khasanov', 'MyKhasanovy1991!'),headers={'X-Atlassian-Token': 'MTA0NDc2OTk3NjkzOolnsvIoPFJQcs5EMXmjj6Qos7pR'}, data=comment, verify=False)
  r2 = requests.get(URL, auth=('e.khasanov', 'MyKhasanovy1991!'),headers={'X-Atlassian-Token': 'MTA0NDc2OTk3NjkzOolnsvIoPFJQcs5EMXmjj6Qos7pR'}, verify=False)
  r2 = r2.content


