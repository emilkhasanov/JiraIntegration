#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# gRPC adapter client (Lartech)
# cd lib/grpc && python3 -m grpc_tools.protoc -Iproto --python_out=. --grpc_python_out=. proto/grpc-adpt.proto
#
# (C) 2020 Egor Babenko, Saint-Petersburg, Russia
# Released under GNU Lesser General Public License (LGPL)
# email: e.babenko@lar.tech
# --------------------------------------------------------------------

from google.protobuf import empty_pb2
from logging_handler import initLogger
import grpc_adpt_pb2, grpc_adpt_pb2_grpc
import os
import grpc
import collections
import uuid
import time
import threading
from utils import *


__author__     = "Egor Babenko"
__copyright__  = "Copyright 2021, Lartech LLC"
__credits__    = []
__license__    = "LGPL"
__version__    = "0.0.8"
__updated__    = "2022-01-28"
__maintainer__ = "Egor Babenko"
__email__      = "e.babenko@lar.tech"
__status__     = "Development"


class DevicePair():
  def __init__(self, deveui, serialRemote=None):
    self.deveui = deveui
    self.serialRemote = serialRemote


class DeviceQuery():
  def __init__(self, devicePair, payload=None, fport=201):
    self.devicePair = devicePair
    self.fport = fport
    self.payload = payload


class Certificate():
  def __init__(self, keysdir, logAppendName=''):
    self.log = initLogger(self, logAppendName)
    self.log.info("Read certificates from folder {0}".format(keysdir))
    self.root = self._loadFile('%s/rootCA.crt' % keysdir)
    self.log.info("Root certificate loaded")
    self.certificate = self._loadFile('%s/certificate.crt' % keysdir)
    self.log.info("Client certificate loaded")
    self.privateKey = self._loadFile('%s/private_key.pem' % keysdir)
    self.log.info("Client private key loaded")

  def _loadFile(self, filepath):
    real_path = os.path.join(os.path.dirname(__file__), filepath)
    with open(real_path, 'rb') as f:
      return f.read()


class MTSafeList():
  def __init__(self):
    self.list = collections.deque()

  def length(self):
    return len(self.list)

  def append(self, elem):
    self.list.append(elem)

  def pop(self):
    return self.list.popleft()


class MsgQueueIterator():
  def __init__(self, msg_queue, logAppendName=''):
    self.log = initLogger(self, logAppendName)
    self.msg_queue = msg_queue
    self.empty_msg = empty_pb2.Empty()
    self.requests = set()

  def __iter__(self):
    return self

  def __next__(self):
    time.sleep(1)
    msg_id = self._getMessageId()
    if self.msg_queue.length() > 0:
      dl_message = self.msg_queue.pop()
      payload = normalizePayload(dl_message.frmpayload)
      request = grpc_adpt_pb2.Request(messageId=msg_id, downlinkMessage=dl_message)
      self.requests.add(msg_id)
      self.log.info('[%s] >>>>> Downlink message id %s sent: (%d, 0x%s) -> [%s]' % (normalizeDeveui(dl_message.devEui[0]), msg_id, dl_message.fport, payload[0:4], payload))
    else:
      request = grpc_adpt_pb2.Request(messageId=msg_id, pingMessage=self.empty_msg)
    return request

  def _getMessageId(self):
    return str(uuid.uuid4()).strip('-')[0:8]


class GrpcAdapterClient():
  def __init__(self, keysdir, url, token, logAppendName=''):
    self.logAppendName = logAppendName
    self.log = initLogger(self, logAppendName)
    self.certificate = Certificate(keysdir, logAppendName)
    self.messageQueue = MTSafeList()
    self.callback = None
    self.channel = None
    self.stub = None
    self.threadEnabled = False
    self.inputStream = None
    self.thread = None
    self.url = url
    self.token = token
    self.log.info("gRPC client initialized")
    self.framecounter = ''

  def startProcessing(self, callback, report_delivered=False):
    self.log.info("gRPC client started")
    self._createStub()
    self.threadEnabled = True
    self.callback = callback
    self.report_delivered = report_delivered
    self.msg_queue_iterator = MsgQueueIterator(self.messageQueue, self.logAppendName)
    self.inputStream = self.stub.streamData(self.msg_queue_iterator)
    self.thread = threading.Thread(target=self._readIncoming)
    self.thread.daemon = False
    self.thread.start()

  def stopProcessing(self, msg = None):
    self.log.info("Processing stopped %s" % ('' if msg is None else 'with message "%s"' % msg))
    self.threadEnabled = False
    self.inputStream = None
    self.thread = None
    if self.channel is not None:
      self.channel.close()
    self.channel = None
    self.stub = None
    time.sleep(3)

  def sendDownlink(self, deviceQuery, confirmed=False):
    deveui = stripDeveui(deviceQuery.devicePair.deveui)
    try:
      payload = normalizePayload(deviceQuery.payload)
      downlink = grpc_adpt_pb2.DownlinkMessage(
        devEui = [deveui],
        token = self.token,
        confirmed = confirmed,
        fport = deviceQuery.fport,
        frmpayload = stringToBytes(payload),
        enableStatusReplies = True
      )
      self.log.info('[%s] Downlink %sconfirmed message appened: (%d, 0x%s) -> [%s]' % (normalizeDeveui(deveui), '' if confirmed else 'un', deviceQuery.fport, payload[0:4], payload))
      self.messageQueue.append(downlink)
    except Exception as err:
      self.log.error('[{0}] Exception on sending downlink: {1}'.format(deveui, err))

  def _createStub(self):
    metadataCred = grpc.metadata_call_credentials(self._callbackMetadataPlugin)
    sslChannelCred = grpc.ssl_channel_credentials(root_certificates=self.certificate.root,
                                                  certificate_chain=self.certificate.certificate,
                                                  private_key=self.certificate.privateKey)
    channelCred = grpc.composite_channel_credentials(sslChannelCred, metadataCred)
    self.channel = grpc.secure_channel(self.url, channelCred)
    self.channel.subscribe(self._callbackChannelStatus, try_to_connect=True)
    self.stub = grpc_adpt_pb2_grpc.GrpcAdapterStub(self.channel)
    self.log.info("gRPC client created to host %s" % self.url)

  def _callbackMetadataPlugin(self, context, callback):
    metadata = [('owner_token', self.token)]
    callback(metadata, None)

  def _callbackChannelStatus(self, arg):
    self.log.info("channel status = %s" % arg)
    return

  def _readIncoming(self):
    try:
      while self.threadEnabled:
        ans = next(self.inputStream)
        self._messageProcessing(ans)
    except grpc._channel._Rendezvous as err:
      self._handleError(err)
    self.log.info("Process finished")

  def _messageProcessing(self, rsp):
    if rsp.WhichOneof("payload") == "downlinkMessageStatus":
      if rsp.correlationId in self.msg_queue_iterator.requests:
        self._downlinkMessageStatus(rsp)
    elif rsp.WhichOneof("payload") == "pingMessage":
      time.sleep(0.1)
    elif rsp.WhichOneof("payload") == "uplinkMessage":
      self._uplinkMessage(rsp)
    else:
      self.log.warn('Unknown message %s' % rsp)

  def _downlinkMessageStatus(self, response):
    statusName = grpc_adpt_pb2.DownlinkMessageStatus.Name(response.downlinkMessageStatus)
    self.log.info("Downlink message %s got status %s callback: %s" % (response.correlationId, statusName, self.callback))
    if statusName in ('UNDEFINED', 'ERROR', 'NOT_AUTHENTICATED', 'REJECTED', 'LOST'):
      self.msg_queue_iterator.requests.discard(response.correlationId)
      if self.callback is not None:
        self.callback(delivered=False)
    elif statusName == 'DELIVERED':
      self.msg_queue_iterator.requests.discard(response.correlationId)
      if self.report_delivered:
        if self.callback is not None:
          self.callback(delivered=True)

  def _uplinkMessage(self, response):
    msg = response.uplinkMessage
    deveui = msg.devEui
    payload = normalizePayload(msg.frmpayload)
    self.frameCounter = msg.frameCounter
    self.log.info("[%s] <<<<< Uplink message received: (%d, 0x%s) -> [%s] calling %s" % (normalizeDeveui(deveui), msg.fport, payload[0:4], payload, self.callback))
    if self.callback is not None:
      self.callback(deveui=msg.devEui, payload=msg.frmpayload, fport=msg.fport)

  def _handleError(self, error):
    self.log.error("Received error: %s" % error)
