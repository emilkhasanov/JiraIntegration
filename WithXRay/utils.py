#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# Utils methods
#
# (C) 2020 Egor Babenko, Saint-Petersburg, Russia
# Released under GNU Lesser General Public License (LGPL)
# email: e.babenko@lar.tech
# --------------------------------------------------------------------


import google.protobuf.wrappers_pb2
import types_pb2
from datetime import datetime
from binascii import b2a_hex
from textwrap import wrap


__author__     = "Egor Babenko"
__copyright__  = "Copyright 2021, Lartech LLC"
__credits__    = []
__license__    = "LGPL"
__version__    = "0.0.2"
__updated__    = "2021-09-08"
__maintainer__ = "Egor Babenko"
__email__      = "e.babenko@lar.tech"
__status__     = "Development"


def intToUInt32(value):
  return google.protobuf.wrappers_pb2.UInt32Value(value=value) if value is not None else value

def intToUInt64(value):
  return google.protobuf.wrappers_pb2.UInt64Value(value=value) if value is not None else value

def stringToStringValue(value):
  return google.protobuf.wrappers_pb2.StringValue(value=value) if value is not None else value

def booleanToBoolValue(value):
  return google.protobuf.wrappers_pb2.BoolValue(value=value) if value is not None else value

def unicastToLoraclass(unicast):
  return types_pb2.LoraClass.Value('A') if unicast.upper() == 'A' else types_pb2.LoraClass.Value('C')

def binaryToRawImage(binaryData):
  return google.protobuf.wrappers_pb2.BytesValue(value=binaryData) if binaryData is not None and len(binaryData) > 0 else None

def uint64ToDate(intValue):
  return datetime.fromtimestamp(intValue.value/1000) if intValue is not None and isinstance(intValue.value, int) and intValue.value > 0 else None

def stripDeveui(deveui):
  return deveui.upper().replace(':', '').strip()

def stringToBytes(payload):
  return bytes(bytearray.fromhex(normalizePayload(payload)))

def normalizeDeveui(deveui):
  return ':'.join(wrap(deveui.upper().strip(), 2))

def normalizePayload(payload):
  _payload = payload
  if (type(payload) is bytes) or (type(payload) is int):
    _payload = b2a_hex(payload).decode('utf-8')
  return _payload.upper().replace(' ', '').strip()
