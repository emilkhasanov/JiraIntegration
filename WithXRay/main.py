#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

"""


import json
import os
import time
import requests
import sys
from urllib3.exceptions import InsecureRequestWarning
from grpc_adapter import GrpcAdapterClient, DeviceQuery, DevicePair
from logging_handler import initLogger
from utils import *
import JiraTests
from JiraTests import WorkWithJira
UpLink = ''

class GrpcClient():
  def __init__(self):
    self.logAppendName = ''
    self.log = initLogger(self, self.logAppendName)

    self.username = 'e.khasanov@lar.tech'
    self.password = 'e.khasanov'
    self.authUrl = 'https://auth.lar.tech/oauth/token'
    self.client = 'e.khasanov'
    self.secret = 'Kuzya_2017'
    grpc_adpt_url = 'grpc.api.lar.tech:9021'

    self.token = self.__getToken()
    self.grpcClient = GrpcAdapterClient('keys', grpc_adpt_url, self.token, logAppendName=self.logAppendName)
    self.threadEnabled:bool = False
    self.sentMessage:bool = False
    self.sentDeveui:str = None
    self.InDevEui:str = '04:97:90:01:F0:08:B6:26'
    self.InPort:int = 201
    self.InCommand:str = '0001'
    self.UpLink:str = ''

  def start(self):
    self.threadEnabled = True
    self.grpcClient.startProcessing(self.upcommingHandler, True)
    while self.threadEnabled:
      self.grpcListener()
      time.sleep(1)

  def sendMessage(self, deveui:str, fport:int=201, payload:str='0001'):
    self.sentDeveui = normalizeDeveui(deveui)
    query = DeviceQuery(DevicePair(self.sentDeveui), payload, fport)
    self.grpcClient.sendDownlink(query, True)

  def stop(self):
    self.threadEnabled = False

  def __getToken(self):
    """Получение токена пользователя"""
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    gtData = {'grant_type': 'password', 'username': self.username, 'password': self.password}
    self.log.info('Grant type data: {0}'.format(gtData))
    self.log.info('Sending request to "{0}" with client "{1}" and secret "{2}"'.format(self.authUrl, self.client, self.secret))
    response = requests.post(self.authUrl, data=gtData, verify=False, auth=(self.client, self.secret))
    try:
      jsonData = json.loads(response.text)
      self.log.info('Got response: {0}'.format(jsonData))
      return jsonData['access_token']
    except Exception as err:
      self.log.error('Exception on load response as JSON: {0}'.format(err))
      return None

  def grpcListener(self):
    # TODO Прервать спустя 60 секунд
    if not self.sentMessage:
      # self.sendMessage('04:97:90:00:21:15:47:E7', 201, "0008")
      self.sendMessage(self.InDevEui, self.InPort, self.InCommand)
      self.sentMessage = True

  def upcommingHandler(self, deveui=None, payload=None, fport=None, delivered=False):
    global UpLink
    """Обработчик ответа отключения автосохранения KVS на устройстве"""
    if deveui is None and payload is None:
      self.log.info(f'Got uplink with delivered {delivered}')
    elif deveui is not None and payload is not None and fport is not None:
      self.log.info(f"[{deveui}] handling uplink on port {fport} with payload: [{normalizePayload(payload)}]")
      my_devEui_1 = self.sentDeveui.replace(":","")
      my_devEui_2 = normalizeDeveui(deveui).replace(":","")
      UpLink = normalizePayload(payload)

      if my_devEui_1 == my_devEui_2:
        self.sentMessage = False
        self.threadEnabled = False

if __name__ == '__main__':
  client = GrpcClient()
  client.start()
  Key = 'QA-13'
  ExecutionContent = WorkWithJira.TestReader(WorkWithJira,Key)
  for x in ExecutionContent:
    steps = WorkWithJira.StepsReader(WorkWithJira, x)[0]
    print(steps)
    test_id = WorkWithJira.StepsReader(WorkWithJira, x)[1]
    print('test_id', test_id)
    test_key = WorkWithJira.StepsReader(WorkWithJira, x)[2]
    print('test_key',test_key)
    Result = []
    for i in range(0, len(steps)):
      FrameCounter = int(client.grpcClient.frameCounter)
      DeltaFrameCounter = 0
      client.InDevEui = '04:97:90:01:F0:08:B6:26'
      client.InCommand = WorkWithJira.CommandSender(WorkWithJira, steps[i])[0]
      client.InPort = int(WorkWithJira.CommandSender(WorkWithJira, steps[i])[1])
      ExpectResult = WorkWithJira.CommandSender(WorkWithJira, steps[i])[2]
      Action = WorkWithJira.CommandSender(WorkWithJira, steps[i])[3]
      print('InCommand         ', client.InCommand, client.InPort, ExpectResult)
      client.grpcListener()
      # time.sleep(1)
      timeout = time.time() + 60 * 3
      if FrameCounter != '':
        while (DeltaFrameCounter < 1):
          DeltaFrameCounter = client.grpcClient.frameCounter - FrameCounter
          if time.time() > timeout:
            break
          print(f'({time.time()} < {timeout})')
      time.sleep(1)
      if DeltaFrameCounter == 0:
        UpLink = 'AbsentUplink'
      else:
        UpLink = UpLink

      asdf = ExpectResult[0].replace(' ', '')
      asdf = asdf.replace('/n', '').split('.')
      print('asdf', asdf)

      print('uplink 2', UpLink)
      command_len = ExpectResult[0].replace(' ', '')
      print('command_len 1', command_len)
      command_len = command_len.replace('/n', '').split('.')
      command_len = command_len[1]
      print('command_len 2', command_len)
      command_len = len(command_len)
      uplink_command = UpLink[:command_len]
      print('uplink_command  ', uplink_command)
      status_code = str(UpLink[command_len:command_len+2])
      print('status_code', status_code)
      # if str(ExpectResult[j_1]) == str(uplink_command):

      WorkWithJira.CommentWriter(WorkWithJira, test_id, str(f'\\ In step N {i+1} Uplink = {str(UpLink)}'))

      for j in range(0, len(ExpectResult)):
        Result.append(WorkWithJira.UpLinkAsserts(WorkWithJira, ExpectResult[j], UpLink, status_code, test_id, i+1))
      LastResult = []
      for k in range(0, len(Result)):
        Cache = Result[k]
        if type(Result[k]) == list:
          for l in range(0, len(Cache)):
            LastResult.append(int(Cache[l]))
        else:
          LastResult.append(int(Cache))
      Result = LastResult
      print('Result', Result)
      WorkWithJira.JiraSender(WorkWithJira, Result, test_id)
      print('Result, ExpectResult, test_key, action', Result, ExpectResult, test_key, Action)

  # client.grpcClient.frameCounter
  # client.InDevEui = '04:97:90:01:F0:08:B6:42'
  # client.InPort = 201
  # client.InCommand = 'F006'
  # client.grpcListener()
  # print(client.UpLink)
  # time.sleep(20)
  # client.InDevEui = '04:97:90:01:F0:08:B6:42'
  # client.InPort = 201
  # client.InCommand = '0008'
  # client.grpcListener()
  # print(client.UpLink)
  sys.exit(0)
  client.stop()

