# coding=utf-8
# Setup Triple Pub Keys
# The person who associated a work with this deed has dedicated
# the work to the public domain by waiving all of his or her rights
# to the work worldwide under copyright law, including all related
# and neighboring rights, to the extent allowed by law.
# You can copy, modify, distribute and perform the work, even for
# commercial purposes, all without asking permission.
# In no way are the patent or trademark rights of any person affected by
# CC0, nor are the rights that other persons may have in the work or in
# how the work is used, such as publicity or privacy rights.
# Unless expressly stated otherwise, the person who associated a work with
# this deed makes no warranties about the work, and disclaims liability
# for all uses of the work, to the fullest extent permitted by applicable law.
# When using or citing the work, you should not imply endorsement by the 
# author or the affirmer.
# https://creativecommons.org/publicdomain/zero/1.0/
import getpass
from Crypto.PublicKey import RSA 
from pathlib import Path
import base64,sys
from os.path import expanduser
from datetime import date,datetime
import paho.mqtt.publish as publish
home = expanduser("~")
try:
  mqtt_broker_hostname=sys.argv[1].rstrip()
except:
  print ('python3 stk.py <hostname/ip of mqtt broker>')
  sys.exit()
if not Path(home+'/triples_priv.pem').exists():
   hname= input("Human readable name (no spaces): ")
   f = open(home+'/triples_name.txt','wt')
   f.write(hname)
   sec=getpass.getpass(prompt='Password: ', stream=None)
   sec2=getpass.getpass(prompt='Password again: ', stream=None)
   if sec==sec2:
      key = RSA.generate(1024)
      encrypted_key = key.export_key(format='PEM',pkcs=8,passphrase=sec)
      f = open(home+'/triples_priv.pem','wb')
      f.write(encrypted_key)
      f.close()
      pub = key.public_key().export_key()
      f = open(home+'/triples_pub.pem','wb')
      f.write(pub)
      f.close()

      print("keys written")
   else:
      print("passwords don't match")
else:
   f = open(home+'/triples_name.txt','rt')
   hname=f.read().strip()
   f = open(home+'/triples_pub.pem','rb')
   pubt=base64.b64encode(f.read())
   ts=datetime.utcnow().isoformat(sep='T', timespec='milliseconds').replace(':','').replace('-','').replace(' ','')+'Z'
   publish.single('all',hname+'🔹🔐🔹'+pubt.decode(),hostname=mqtt_broker_hostname)
