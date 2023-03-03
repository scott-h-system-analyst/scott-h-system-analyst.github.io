# coding=utf-8
# Triples ReceiVe
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
from os.path import expanduser
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA 
from Crypto.Signature import pkcs1_15 
import base64,sqlite3
import base64,sys,os,time
import paho.mqtt.client as mqttc
from datetime import date,datetime
import pygraphviz as pgv

try:
  mqtt_broker_hostname=sys.argv[1].rstrip()
  mode=sys.argv[2].rstrip()
  g=sys.argv[3].rstrip()
  p=sys.argv[4].rstrip()
except:
  print ('python3 trv.py <hostname/ip of mqtt broker> <replay or mqtt> <graph> <pause seconds>')
  sys.exit()
def efo(p):
  if p=='↔️':
    return 'both'
  if p=='➡️':
    return 'forward'
  if p=='⬅️':
    return 'back'
G={}
home = expanduser("~")
conn=sqlite3.connect('graph.db')
conn.execute('create table if not exists gs(ts text,id text,graph text,sub text, pred text,obj text)')
conn.execute('create index if not exists i on gs(ts)')
#cursor = conn.cursor()
if mode=='mqtt':
  conn.execute('delete from gs')
#conn.commit()
#cursor.close()
G[g] = pgv.AGraph(directed=True)
options='-Epenwidth=2 -Npenwidth=2 -Nfontname="sans-serif" -Gsize="13,9" -Gmargin=".25" -Goverlap="prism"' 
options+=' -Ecolor="#888888" -Gsplines=true -Gsep="+5"'

if mode=='replay':
  cursor = conn.cursor()
  for row in cursor.execute('select * from gs where graph="'+g+'" order by ts'):
    print(row)
    if row[4]=='⛔️':
      if G[g].has_edge(row[3],row[5]):
        G[g].remove_edge(row[3],row[5])
    else:
      G[g].add_edge(row[3],row[5],dir=efo(row[4]))
    G[g].draw(home+'/tmp/'+g+'.png',prog='neato',args=options)
    os.system('kitty +kitten icat '+home+'/tmp/'+g+'.png')
    time.sleep(int(p))




def on_message(client, userdata, msg):
  if mode=='mqtt':
    cursor = conn.cursor()
    m=msg.payload.decode('utf-8')
    ts=datetime.utcnow().isoformat(sep='T', timespec='milliseconds').replace(':','').replace('-','').replace(' ','')+'Z'
    triple=m.split('🔹')
    if triple[1]=='✨' or triple[1]=='⛰️':
      mess,sig=triple[2].split('🔸') 
      h = SHA256.new(bytearray(mess,'utf8'))
      try:
        pub = RSA.import_key(open(home+'/ids/'+triple[0]+'_triples_pub.pem').read())
        pkcs1_15.new(pub).verify(h, base64.b64decode(bytearray(sig,'utf8')))
        tri=base64.b64decode(bytearray(mess,'utf8')).decode('utf-8')
        gs,p,o=tri.split('🔹')
        if gs.split('▪️')[0]==g:
          print('✅✨: '+triple[0]+' - '+tri)
          s=gs.split('▪️')[1]
          cursor.execute('''
            insert into gs(ts,id,graph,sub,pred,obj)
            values (?,?,?,?,?,?);
            ''',
            (ts,triple[0],g,s,p,o))
          conn.commit()
          if g not in G:
            G[g] = pgv.AGraph(directed=True)
          if G[g].has_edge(s,o):
            G[g].remove_edge(s,o)
          G[g].add_edge(s,o,dir=efo(p))
          G[g].draw(home+'/tmp/'+g+'.png',prog='neato',args=options)
          os.system('kitty +kitten icat '+home+'/tmp/'+g+'.png')
      except ValueError:
        print('🛑✨: '+triple[0]+' - '+base64.b64decode(bytearray(mess,'utf8')).decode('utf-8'))
    elif triple[1]=='⛔️':
      mess,sig=triple[2].split('🔸') 
      h = SHA256.new(bytearray(mess,'utf8'))
      try:
        pub = RSA.import_key(open(home+'/ids/'+triple[0]+'_triples_pub.pem').read())
        pkcs1_15.new(pub).verify(h, base64.b64decode(bytearray(sig,'utf8')))
        tri=base64.b64decode(bytearray(mess,'utf8')).decode('utf-8')
        gs,p,o=tri.split('🔹')
        if gs.split('▪️')[0]==g:
          print('✅⛔️: '+triple[0]+' - '+base64.b64decode(bytearray(mess,'utf8')).decode('utf-8'))
          s=gs.split('▪️')[1]
          cursor.execute('''
            insert into gs(ts,id,graph,sub,pred,obj)
            values (?,?,?,?,?,?);
            ''',
            (ts,triple[0],g,s,'⛔️',o))
          conn.commit()
          if G[g].has_edge(s,o):
            G[g].remove_edge(s,o)
          G[g].draw(home+'/tmp/'+g+'.png',prog='neato',args=options)
          os.system('kitty +kitten icat '+home+'/tmp/'+g+'.png')
      except ValueError:
        print('🛑⛔️: '+triple[0]+' - '+base64.b64decode(bytearray(mess,'utf8')).decode('utf-8'))

 
if mode=='mqtt':
  client = mqttc.Client()
  client.on_message = on_message
  client.connect(mqtt_broker_hostname, 1883, 60)
  client.subscribe("all")
  client.loop_forever()
