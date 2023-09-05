#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from requests.auth import HTTPBasicAuth
import codecs
import binascii
import time
import new
from new import CommentWriter
# from jira.client import JIRA

class WorkWithJira():
  def __init__(self):
    self.username = 'e.khasanov'
    self.password = 'MyKhasanovy1991!'
    self.execution_key = ''
    self.my_token = 'MTA0NDc2OTk3NjkzOolnsvIoPFJQcs5EMXmjj6Qos7pR'

  def TestReader(self, in_execution_key):
    self.execution_key = in_execution_key
    URL = f'https://jira.lar.tech/rest/raven/1.0/api/testexec/{in_execution_key}/test'
    response = requests.get(URL,  auth=('e.khasanov', 'MyKhasanovy1991!'), headers= {'X-Atlassian-Token':'MTA0NDc2OTk3NjkzOolnsvIoPFJQcs5EMXmjj6Qos7pR'}, verify=False)
    r = response.content
    d = json.loads(r)
    return(d)

  def StepsReader(self, in_execution_content):
    # for x in in_execution_content:
    test_attributes = in_execution_content
    test_key = str(test_attributes['key'])
    test_id = str(test_attributes['id'])
    print(test_key)
    URL = f'https://jira.lar.tech/rest/api/2/issue/{test_key}'
    r = requests.get(URL,  auth=('e.khasanov', 'MyKhasanovy1991!'), headers= {'X-Atlassian-Token':'MTA0NDc2OTk3NjkzOolnsvIoPFJQcs5EMXmjj6Qos7pR'}, verify=False)
    r = r.content
    d = json.loads(r)
    d = d['fields']
    steps = d['customfield_10304']
    steps = steps['steps']

    return [steps, test_id, test_key]

  def CommandSender(self, all_steps):
    # for i in range(0, len_1):
    result = []
    a = all_steps#[i]
    b = a['fields']
    data = b['Data']
    data_lst = data.replace(' ', '')
    data_lst = data.replace('/n', '').split()
    ExpRes = b['Expected Result']
    ExpRes = ExpRes.replace(' ', '')
    Explst = ExpRes.replace('/n', '').split()
    Action = b['Action']
    Action = Action.replace(' ', '')
    Action = Action.replace('/n', '').split()
    return [data_lst[1], data_lst[3], Explst, Action]

    # print(f'send command {data_lst[1]} to port {data_lst[3]}')

  def UpLinkAsserts(self, In_Explst, uplink, status_code_in, test_id_in, action):

    result = []
    exp_assert = In_Explst.replace(',', '.')
    exp_assert = exp_assert.replace('.', ' ')
    exp_assert = exp_assert.replace('.', ' ').split()
    comment = []
    action = str(action)
    print(exp_assert)
    print(exp_assert[0])
    print('test_id_in', test_id_in)

    if str(uplink) != 'AbsentUplink':
      if str(exp_assert[0]) == '1':
        print('str(exp_assert[0]) == 1')
        for n in range(1, len(exp_assert)):
          if str(exp_assert[n]) in str(uplink):
            print(f'{str(exp_assert[n])} in {str(uplink)}')
            result.append(1)
          else:
            print(f'{str(exp_assert[n])} not in {str(uplink)}')
            result.append(0)
            comment.append(f'Invalid result {exp_assert[0]}.{str(exp_assert[n])}/n')
            self.CommentWriter(self, test_id_in, str(f'\\ In step N {action} - {str(comment)}'))

      if str(exp_assert[0]) == '2':
        print('str(exp_assert[0]) == 2')
        for n in range(1, len(exp_assert)):
          if str(exp_assert[n]) in str(uplink):
            print(f'{str(exp_assert[n])} in {str(uplink)}')
            result.append(1)
          else:
            print(f'{str(exp_assert[n])} not in {str(uplink)}')
            result.append(0)
            comment.append(f'Invalid result {exp_assert[0]}.{str(exp_assert[n])}/n')
            self.CommentWriter(self, test_id_in, str(f'\\ In step N {action} - {str(comment)}'))

      if str(exp_assert[0]) == '3':
        print('str(exp_assert[0]) == 3')
        for n in range(1, len(exp_assert)):
          ex_results_ascii = str(exp_assert[n])
          ex_results_ascii = str(codecs.encode(ex_results_ascii.encode('ascii')   , 'hex'))
          ex_results_ascii = ex_results_ascii[2:(len(ex_results_ascii)-1)]
          if str(ex_results_ascii) in str(uplink):
            print(f'{str(exp_assert[n])} in {str(uplink)}')
            result.append(1)
          else:
            print(f'{str(exp_assert[n])} not in {str(uplink)}')
            result.append(0)
            comment.append(f'Invalid result {exp_assert[0]}.{str(exp_assert[n])}/n')
            self.CommentWriter(self, test_id_in, str(f'\\ In step N {action} - {str(comment)}'))

      if str(exp_assert[0]) == '4':
        print('str(exp_assert[0]) == 4')
        for n in range(1, len(exp_assert)):
          if str(exp_assert[n]) in str(status_code_in):
            print(f'{str(exp_assert[n])} in {str(status_code_in)}')
            result.append(1)
          else:
            print(f'{str(exp_assert[n])} not in {str(status_code_in)}')
            result.append(0)
            comment.append(f'Invalid result {exp_assert[0]}.{str(exp_assert[n])}/n')
            self.CommentWriter(self, test_id_in, str(f'\\ In step N {action} - {str(comment)}'))

      if str(exp_assert[0]) == '5':
        print('str(exp_assert[0]) == 5')
        for n in range(1, len(exp_assert)):
          if str(exp_assert[n]) == str(len(uplink)):
            print(f'{str(exp_assert[n])} in {str(len(uplink))}')
            result.append(1)
          else:
            print(f'{str(exp_assert[n])} not in {str(len(uplink))}')
            result.append(0)
            comment.append(f'Invalid result {exp_assert[0]}.{str(exp_assert[n])}/n')
            self.CommentWriter(self, test_id_in, str(f'\\ In step N {action} - {str(comment)}'))

      if str(exp_assert[0]) == '6':
        print('str(exp_assert[0]) == 6')
        for n in range(1, len(exp_assert)):
          exp_assert_list = exp_assert[n].replace('=', ' ').split()
          print('sexp_assert_list___', exp_assert_list)
          print(f'if {str(uplink[int(exp_assert_list[0]) - 1])} == {str(exp_assert_list[1])}:')
          if str(uplink[int(exp_assert_list[0])-1]) == str(exp_assert_list[1]):
            print(f'{str(exp_assert[n])} in {str(len(uplink))}')
            result.append(1)
          else:
            print(f'{str(exp_assert[n])} not in {str(len(uplink))}')
            result.append(0)
            comment.append(f'Invalid result {exp_assert[0]}.{str(exp_assert[n])}/n')
            self.CommentWriter(self, test_id_in, str(f'\\ In step N {action} - {str(comment)}'))

    else:
      result.append(0)
      comment.append(f'Invalid result because {uplink}/n')
      self.CommentWriter(self, test_id_in, str(f'\\ In step N {action} - {str(comment)}'))


    return result

  def JiraSender(self, result, test_id):
    print('test_id', test_id)
    if 0 in result:
      URL = f'https://jira.lar.tech/rest/raven/1.0/api/testrun/{test_id}/status?status=FAIL'
      r = requests.put(URL,  auth=('e.khasanov', 'MyKhasanovy1991!'), headers= {'X-Atlassian-Token':'MTA0NDc2OTk3NjkzOolnsvIoPFJQcs5EMXmjj6Qos7pR'}, verify=False)
    else:
      URL = f'https://jira.lar.tech/rest/raven/1.0/api/testrun/{test_id}/status?status=PASS'
      r = requests.put(URL,  auth=('e.khasanov', 'MyKhasanovy1991!'), headers= {'X-Atlassian-Token':'MTA0NDc2OTk3NjkzOolnsvIoPFJQcs5EMXmjj6Qos7pR'}, verify=False)

  def CommentWriter(self, test_id_input, comment_input):
    test_id_input = int(test_id_input)
    comment = []
    URL = f'https://jira.lar.tech/rest/raven/1.0/api/testrun/{test_id_input}/comment'
    r2 = requests.get(URL, auth=('e.khasanov', 'MyKhasanovy1991!'),
                      headers={'X-Atlassian-Token': 'MTA0NDc2OTk3NjkzOolnsvIoPFJQcs5EMXmjj6Qos7pR'}, verify=False)
    r2 = r2.content
    if 'raw' not in str(r2):
      d = ''
    else:
      d = json.loads(r2)
      d = d['raw']
    comment.append(d)
    comment.append(comment_input)
    comment = str(comment).replace('[', '').replace(']', '').replace('\\', '').replace('"', '').replace("'", '').replace('/n', '\\').replace('/', '').replace(',', '').replace('In step', '\\\In step')
    comment = str(comment)
    r2 = requests.put(URL, auth=('e.khasanov', 'MyKhasanovy1991!'),
                      headers={'X-Atlassian-Token': 'MTA0NDc2OTk3NjkzOolnsvIoPFJQcs5EMXmjj6Qos7pR'}, data=comment,
                      verify=False)
    r2 = requests.get(URL, auth=('e.khasanov', 'MyKhasanovy1991!'),
                      headers={'X-Atlassian-Token': 'MTA0NDc2OTk3NjkzOolnsvIoPFJQcs5EMXmjj6Qos7pR'}, verify=False)
    r2 = r2.content




