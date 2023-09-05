#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# Log handler (Lartech)
#
# (C) 2020 Egor Babenko, Saint-Petersburg, Russia
# Released under GNU Lesser General Public License (LGPL)
# email: e.babenko@lar.tech
# --------------------------------------------------------------------


import logging


__author__     = "Egor Babenko"
__copyright__  = "Copyright 2021, Lartech LLC"
__credits__    = []
__license__    = "LGPL"
__version__    = "0.0.1"
__updated__    = "2021-09-08"
__maintainer__ = "Egor Babenko"
__email__      = "e.babenko@lar.tech"
__status__     = "Development"


def initLogger(target, logAppendName=''):
  logFormat = '%(asctime)s %(levelname)s [%(threadName)s] %(name)s.%(funcName)s: %(message)s'

  logger = logging.getLogger(target.__class__.__name__)
  logger.setLevel(logging.DEBUG)
  logger.handlers = []
  logger.propagate = 0

  formatter = logging.Formatter(logFormat)

  consoleHandler = logging.StreamHandler()
  consoleHandler.setLevel(logging.INFO)
  consoleHandler.setFormatter(formatter)
  logger.addHandler(consoleHandler)

  fileHandler = logging.FileHandler(filename='grpc-client%s.log' % logAppendName, mode='a')
  fileHandler.setLevel(logging.DEBUG)
  fileHandler.setFormatter(formatter)
  logger.addHandler(fileHandler)

  return logger
