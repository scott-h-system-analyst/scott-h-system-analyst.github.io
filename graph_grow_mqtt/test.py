# coding=utf-8
import paho.mqtt.client as mqttc
import paho.mqtt.publish as publish
from time import sleep 
client = mqttc.Client(transport='websockets')      
client.connect('localhost', 9001, 60)
triples='''👤🔸Cust🔹🏷🔹ACME\\nCustomers
💽🔸1🔹🏷🔹HQ\\nDigital\\nData
👤🔸Ops🔹🏷🔹Operations
👤🔸Leads🔹🏷🔹Customer\\nLeads
👤🔸Sales🔹🏷🔹Marketing\\nand\\nSales
👤🔸Acct🔹🏷🔹Accounting
👤🔸Execs🔹🏷🔹Executives
👤🔸CstS🔹🏷🔹Customer\\nSupport
👤🔸EnvM🔹🏷🔹Environmental\\nMeasurements
💽🔸2🔹🏷🔹HQ\\nAlternate\\nMedia
👤🔸OOps🔹🏷🔹Oceanic\\nOperations
👤🔸Ship🔹🏷🔹Shipping\\nand\\nLogistics
👤🔸HospP🔹🏷🔹Hospital\\nSupply\\nPartner
👤🔸Prdct🔹🏷🔹Product\\nTeam
👤🔸EngUS🔹🏷🔹Engineering\\nUSA
👤🔸EngIn🔹🏷🔹Engineering\\nIndia
💽🔸3🔹🏷🔹Product\\nDevelopment
👤🔸FldS🔹🏷🔹Field\\nSales
⚗️🔸5🔹🏷🔹Telephonic
⚗️🔸4🔹🏷🔹Customer\\nSupport
⚗️🔸3🔹🏷🔹Partner\\nServices
⚗️🔸2🔹🏷🔹Customer\\nServices
⚗️🔸1🔹🏷🔹Accounting\\nServices
⚗️🔸6🔹🏷🔹Customer\\nRelationship\\nManager
⚗️🔸7🔹🏷🔹Field Sales
⚗️🔸9🔹🏷🔹Business\\nIntelligence\\nand\\nManagement
⚗️🔸8🔹🏷🔹Product\\nAcceptance
⚗️🔸10🔹🏷🔹Operational\\nIntelligence\\nand\\nManagement
⚗️🔸11🔹🏷🔹Product\\nDevelopment
⚗️🔸1🔹↔️🔹👤🔸Acct
⚗️🔸1🔹↔️🔹💽🔸1
⚗️🔸1🔹↔️🔹👤🔸Cust
⚗️🔸2🔹↔️🔹💽🔸1
⚗️🔸2🔹↔️🔹👤🔸Cust
⚗️🔸2🔹↔️🔹👤🔸Ops
⚗️🔸2🔹➡️🔹👤🔸Leads
⚗️🔸3🔹↔️🔹💽🔸1
⚗️🔸3🔹↔️🔹👤🔸HospP
⚗️🔸3🔹↔️🔹💽🔸2
⚗️🔸3🔹↔️🔹👤🔸OOps
⚗️🔸3🔹↔️🔹👤🔸Ship
⚗️🔸3🔹↔️🔹👤🔸Ops
⚗️🔸3🔹↔️🔹👤🔸EnvM
⚗️🔸4🔹↔️🔹💽🔸1
⚗️🔸4🔹↔️🔹💽🔸2
⚗️🔸4🔹↔️🔹👤🔸CstS
⚗️🔸4🔸↔️🔸👤🔸CstS🔹🏷🔹Tickets
⚗️🔸4🔹↔️🔹👤🔸Cust
⚗️🔸5🔹↔️🔹👤🔸CstS
⚗️🔸5🔹↔️🔹👤🔸Cust
⚗️🔸6🔹↔️🔹👤🔸FldS
⚗️🔸6🔹↔️🔹💽🔸1
⚗️🔸6🔹↔️🔹👤🔸Leads
⚗️🔸6🔹↔️🔹👤🔸Sales
⚗️🔸6🔹➡️🔹⚗️🔸8
⚗️🔸7🔹↔️🔹👤🔸FldS
⚗️🔸7🔹↔️🔹💽🔸2
⚗️🔸7🔹↔️🔹👤🔸Leads
⚗️🔸8🔹↔️🔹⚗️🔸10
⚗️🔸8🔹↔️🔹👤🔸EngIn
⚗️🔸8🔹↔️🔹👤🔸Prdct
⚗️🔸8🔹↔️🔹💽🔸3
⚗️🔸8🔹↔️🔹👤🔸EngUS
⚗️🔸9🔹↔️🔹👤🔸Acct
⚗️🔸9🔹↔️🔹💽🔸1
⚗️🔸9🔹↔️🔹👤🔸Execs
⚗️🔸9🔹↔️🔹👤🔸Sales
⚗️🔸10🔹↔️🔹👤🔸Acct
⚗️🔸10🔹↔️🔹💽🔸1
⚗️🔸10🔹↔️🔹👤🔸CstS
⚗️🔸10🔹↔️🔹👤🔸Execs
⚗️🔸10🔹↔️🔹👤🔸Sales
⚗️🔸10🔹↔️🔹👤🔸Ops
⚗️🔸11🔹↔️🔹👤🔸EngIn
⚗️🔸11🔹↔️🔹👤🔸Prdct
⚗️🔸11🔹↔️🔹💽🔸2
⚗️🔸11🔹↔️🔹💽🔸3
⚗️🔸11🔹↔️🔹👤🔸EngUS'''
for l in triples.split('\n'):
  sleep(2)
  publish.single('all',l)
