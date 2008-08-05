#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# P2P framework for simple, non-anonymous network
# building from known nodes
#
# tslocum@gmail.com
# http://www.tj9991.com
# http://code.google.com/p/kaishi/

__author__ = 'Trevor "tj9991" Slocum'
__license__ = 'GNU GPL v3'

import md5
import time
import base64
import sys
import urllib
import zlib
import pickle
import thread
import socket

class kaishi(object):
  def __init__(self):
    # Set all defaults
    socket.setdefaulttimeout(5)
    self.debug = False
    self.nicks = {}
    self.pings = {}
    self.peers = []
    self.uidlist = []
    self.provider = 'http://vector.cluenet.org/~tj9991/provider.php'
    self.host = urllib.urlopen('http://www.showmyip.com/simple/').read()
    self.port = 44545
    self.peerid = self.host + ':' + str(self.port)

    self.handleIncomingData = None
    self.handleAddedPeer = None
    self.handlePeerNickname = None
    self.handleDroppedPeer = None

  def start(self):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.socket.bind(('', self.port))
    thread.start_new_thread(self.receiveData, ())
    thread.start_new_thread(self.pingAllPeers, ())
    thread.start_new_thread(self.pingProvider, ())
    self.fetchPeersFromProvider()

  def sendData(self, identifier, message, **kwargs):
    args = {'uid': None,
            'origin': self.peerid,
            'to': None,
            'bounce': True}
    args.update(kwargs)

    if not args['uid']:
      uid = self.makeID(message)
      self.debugMessage('Making uid for ' + message)
    else:
      uid = args['uid']
    self.uidlist.append(uid)
    if args['bounce']:
      bounce = '1'
    else:
      bounce = '0'
    
    data = identifier + ':' + bounce + ':' + uid + ':' + base64.encodestring(args['origin']) + ':' + message

    data = zlib.compress(unicode(data), 9)
    
    if args['to']:
      try:
        self.socket.sendto(data, self.peerIDToTuple(args['to']))
      except:
        self.dropPeer(args['to'])
        return False
      return True
    else:
      for peer in self.peers:
        try:
          self.socket.sendto(data, self.peerIDToTuple(peer))
        except:
          self.dropPeer(peer)
          return False
      return True

  def receiveData(self):
    while 1:
      data = None
      try:
        data, address = self.socket.recvfrom(65536)
        data = zlib.decompress(data)
        bouncer_peerid = address[0] + ':' + str(address[1]) # peerid of the last bounce
        identifier, bounce, uid, origin, message = data.split(':', 4)
        peerid = base64.decodestring(origin)
      except socket.timeout:
        pass
      except:
        self.debugMessage('Failed to establish a connection.')
        pass
      
      if data and uid not in self.uidlist:
        if peerid not in self.peers and identifier != 'JOIN' and identifier != 'DROP':
          self.addPeer(peerid)
          self.debugMessage('Adding ' + peerid + ' from outside message')
        if identifier == 'JOIN': # a user requests that they join the network
          self.addPeer(peerid)
          self.setPeerNickname(peerid, message) # add the nick sent in the JOIN message
          print 'setting peer nickname of ' + peerid + ' to ' + message
          self.sendData('PEERS', self.makePeerList(), to=peerid, bounce=False)
        elif identifier == 'PEERS': # list of connected peers
          peers = pickle.loads(message)
          for peer, peer_nick in peers.items():
            self.addPeer(peer)
            self.setPeerNickname(peer, peer_nick)
          self.debugMessage('Got peerlist from ' + peerid)
        elif identifier == 'DROP':
          self.dropPeer(peerid)
        elif identifier == 'PING':
          if peerid in self.pings:
            self.pings.update({peerid: time.time()})
          self.debugMessage('Got PING from ' + peerid)
        elif identifier == 'NICK':
          self.setPeerNickname(peerid, message)
        else:
          self.handleIncomingData(peerid, identifier, uid, message)

        if bounce == '1':
          self.sendData(identifier, message, uid=uid, origin=peerid)
      elif data:
        self.debugMessage('Not rerouting data: ' + data)

  def addPeer(self, peerid):
    result = False
    if not peerid in self.peers and peerid != self.peerid:
      self.peers.append(peerid)
      result = self.sendData('JOIN', self.getPeerNickname(self.peerid)) # send our nickname in the message of JOIN
      self.debugMessage('Added peer: ' + self.getPeerNickname(peerid))
      if not result:
        self.dropPeer(peerid)
        
    try:
      if result:
        self.handleAddedPeer(peerid)
    except:
      pass
    
    return result

  def dropPeer(self, peerid):
    if peerid in self.peers and peerid != self.peerid:
      del self.peers[self.peers.index(peerid)]
      self.debugMessage(self.getPeerNickname(peerid) + ' has dropped from network')

      try:
        self.handleDroppedPeer(peerid)
      except:
        pass
        
  def getAllPeersExcept(self, exclude_peerid):
    peers = []
    for peerid in self.peers:
      if peerid != exclude_peerid:
        peers.append(peerid)
    return peers

  def getPeerNickname(self, peerid):
    if peerid in self.nicks:
      return self.nicks[peerid]
    else:
      return peerid

  def setPeerNickname(self, peerid, nickname):
    try:
      self.handlePeerNickname(peerid, nickname)
    except:
      pass
    
    self.nicks.update({peerid: nickname})
    self.debugMessage('Set nickname for ' + peerid + ' to ' + nickname)

  def sendDropNotice(self):
    self.sendData('DROP', 'DROP')

  def pingAllPeers(self):
    for peerid in self.peers:
      if peerid in self.pings:
        if time.time() - self.pings[peerid] >= 20:
          self.dropPeer(peerid)
          self.debugMessage('Dropping ' + self.getPeerNickname(peerid) + ' (no ping responses for 20 seconds)')
      else:
        self.pings.update({peerid: time.time()})
      self.sendData('PING', 'PING', to=peerid, bounce=False)
    time.sleep(15)
    thread.start_new_thread(self.pingAllPeers, ())

  def pingProvider(self):
    time.sleep(60)
    urllib.urlopen(self.provider).read()
    thread.start_new_thread(self.pingProvider, ())
    
  def makePeerList(self):
    peers = {}
    for peerid in self.peers:
      peers.update({peerid: self.getPeerNickname(peerid)})
    
    return pickle.dumps(peers)

  def fetchPeersFromProvider(self):
    self.debugMessage('Fetching peers from provider')
    added_nodes = 0
    known_nodes = urllib.urlopen(self.provider).read()
    if known_nodes != '':
      known_nodes = known_nodes.split('\n')
      for known_node in known_nodes:
        if known_node != '':
          added_nodes += 1
          self.addPeer(known_node)
          self.debugMessage('Added ' + known_node + ' from provider')

  def debugMessage(self, message):
    if self.debug:
      print message
      
  def gracefulExit(self):
    self.sendDropNotice()
    self.socket.close()
    sys.exit()

  def peerIDToTuple(self, peerid):
    host, port = peerid.rsplit(':', 1)
    if host.startswith('['):
      host = host[1:len(host)-1]
    return (host, int(port))

  def makeID(self, data):
    m = md5.new()
    m.update(str(time.time()))
    m.update(str(data))
    return base64.encodestring(m.digest())[:-3].replace('/', '$')

if __name__=='__main__':
  print 'Running this file on its own will not do anything.  Please execute kaishi_chat.py instead.'
