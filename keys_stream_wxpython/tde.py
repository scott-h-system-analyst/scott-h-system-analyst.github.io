# coding=utf-8
# Triple pub Data flow diagram Editor
import urllib.parse,re,json,re,pydash,os
import wx,wx.html2,wx.grid,time,xxhash
from grapheme import graphemes as a #a=atoms
from os.path import expanduser
import base64,sys,getpass
import paho.mqtt.publish as publish
import pygraphviz as pgv
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA 
from Crypto.Signature import pkcs1_15
try:
  mqtt_broker_hostname=sys.argv[1].rstrip()
except:
  print ('python3 tde.py <hostname/ip of mqtt broker>')
  sys.exit()

sec=getpass.getpass(prompt='Password: ', stream=None)
def vl(dct,path):
  if pydash.objects.get(dct,path):
    return list(pydash.objects.get(dct,path))[-1]
  else:
    return ''
base='http://localhost:4029/'
home = expanduser("~")
clear_cache="rm -rf '"+home+"/.cache/tde.py';rm -rf '"+home+"/.local/share/webkitgtk'"
full={}
colr={'orange':'#EE7733','blue':'#0077BB','cyan':'#33BBEE','magenta':'#EE3377',
    'red':'#CC3311','teal':'#009988','grey':'#BBBBBB','black':'#000000'}
#palette for color blindness from https://personal.sron.nl/~pault/
colr_lighter={'orange':'#ffd6bc','magenta':'#fcf1f5','cyan':'#e4fcff'}
predicates=list(a('➡️⬅️↔️'))
properties=list(a('🏷🗨📒'))
G={}
nav={
"wclck":{"s":True,"e":"wait for click"},
"func":{"s":"🏁🏁🏁🏁🏁🏁🏁🏁","e":"last function location"},
"level":{"s":['0'],"e":"current level (graph)"},
"ldnav":{"s":False,"e":"loading navigation"},
"proc":{"s":'1',"e":"highlighted nav['proc']['s']"},
"ldsvg":{"s":False,"e":"loading svg"}
}
with open(home+'/triples_name.txt','rt') as f:
  hname=f.read().strip()
with open(home+'/triples_priv.pem') as f:
      priv = RSA.import_key(f.read(),passphrase=sec)

def efo(p):
  if p=='↔️':
    return 'both'
  if p=='➡️':
    return 'forward'
  if p=='⬅️':
    return 'back'

class edt_frm(wx.Frame):
  def __init__(self):
    wx.Frame.__init__(self, None,wx.ID_ANY,'Triple.Pub - Data Flow Editor',size=(1920,1057))
    trp_pnl = wx.Panel(self)
    trp_pnl.SetBackgroundColour(wx.Colour('#ccffcc'))
    cnt_hsz = wx.BoxSizer(wx.HORIZONTAL)
    cmt_txt = wx.TextCtrl(trp_pnl,size=wx.Size(640,50),style = wx.TE_MULTILINE)
    nar_txt = wx.TextCtrl(trp_pnl,size=wx.Size(640,100),style = wx.TE_MULTILINE)
    nid_txt = wx.TextCtrl(trp_pnl,size=wx.Size(120,35))
    nlb_txt = wx.TextCtrl(trp_pnl,size=wx.Size(355,35))
    nav_web = wx.html2.WebView.New(trp_pnl,size=(158,35))
    dat_grd = wx.grid.Grid(trp_pnl)
    dat_grd.CreateGrid(34,3)
    dat_grd.HideRowLabels()
    dat_grd.HideColLabels()
    dat_grd.SetColSize(0,307)
    dat_grd.SetColSize(1,26)
    dat_grd.SetColSize(2,307)
    dat_grd.EnableEditing(False)
    gra_web = wx.html2.WebView.New(trp_pnl,size=(1300,1052))
    gra_web.EnableHistory(enable=False)
    top_hsz = wx.BoxSizer(wx.HORIZONTAL)
    lft_vsz = wx.BoxSizer(wx.VERTICAL)
    rit_vsz = wx.BoxSizer(wx.VERTICAL)
    cnt_hsz.Add(nid_txt,0,wx.RIGHT,2)
    cnt_hsz.Add(nlb_txt,0,wx.RIGHT,2)
    cnt_hsz.Add(nav_web,0,wx.LEFT,2)
    lft_vsz.Add(cnt_hsz,)
    lft_vsz.Add(cmt_txt,1,wx.TOP|wx.BOTTOM,2)
    lft_vsz.Add(nar_txt)
    lft_vsz.Add(dat_grd,1,wx.TOP,2)
    rit_vsz.Add(gra_web, 1, wx.EXPAND|wx.ALL, 1)
    top_hsz.Add(lft_vsz,1,wx.LEFT|wx.TOP|wx.BOTTOM|wx.EXPAND,2)
    top_hsz.Add(rit_vsz,1,wx.ALL|wx.EXPAND,2)
    trp_pnl.SetSizer(top_hsz)
    arrows = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
    arrows.SetPointSize(13)
    def clear_columns(cols):
      for i in range(34):
        for j in cols:
          if j==1:
            dat_grd.SetCellFont(i,j,arrows)
          dat_grd.SetCellValue(i,j,"")
          dat_grd.SetCellBackgroundColour(i,j,'#ffffff') 
    def create_nav(path):
      nav_html='''<!doctype html>
<html lang="en">
<head>
<meta HTTP-EQUIV='Content-Type' CONTENT='text/html; charset=utf-8'>
<link rel="stylesheet" type="text/css" href="tiny.css" />
</head>
<body><div class="hrefs">~~hrefs~~</div></body>
</html>'''
      href_base_gs='0'
      href_base_tri='0'
      hrefs='<a href="nav.html#'+href_base_tri+'.svg" title="'+href_base_gs+'">0</a>'
      for i in path[2:]:
        href_base_gs+='.'+i
        href_base_tri+='🔸'+i
        hrefs+='.<a href="nav.html#'+href_base_tri+'.svg" title="'+href_base_gs+'">'+i+'</a>'
      return nav_html.replace('~~hrefs~~',hrefs)
    clear_columns([0,1,2])
    with open('index.html') as page:
      pg=page.read()
      triples=re.search('let triples=`(.+?)`',pg,re.DOTALL).group(1)
    lines=triples.split('\n')
    for l in lines:
      q=l.split('▪️')
      [s,p,o]=q[1].split('🔹')
      if p in predicates+properties and s.find('🎛️')==-1:
        s==''
        if s=='':
          pydash.objects.set_with(full,[q[0],p,o],'',{})
        else:
          pydash.objects.set_with(full,[q[0],s,p,o],'',{})
        if p in predicates:
          mess=base64.b64encode(bytearray(l,"utf8")).decode('utf-8')
          h = SHA256.new(bytearray(mess,"utf8"))
          signature = base64.b64encode(pkcs1_15.new(priv).sign(h)).decode('utf-8')
          publish.single('all',hname+'🔹⛰️🔹'+mess+'🔸'+signature)

    nav['ldnav']['s']=True
    nav_web.SetPage(create_nav(nav['level']['s']),base)
    def refresh(path):
      rows=[] 
      nav['func']['s']='✨ refresh'
      clear_columns([0,1,2])
      dat_grd.MakeCellVisible(1,0)
      os.system(clear_cache)
      pstr='🔸'.join(path)
      G[pstr] = pgv.AGraph(directed=True)
      cur=pydash.objects.get(full,pstr)
      #This is the current node, as selected on the left pane
      nid_txt.SetValue(nav['proc']['s'])
      #set node id to navigated
      j=i=0
      if '📒' in cur:
        nar_txt.SetValue(vl(cur,['📒']))
      #set narration if it exists for node
      else:
        nar_txt.SetValue('')
      for k in cur:
        if k not in properties+predicates and k.count('🔸')==1:
          #We want to look at nodes, not properties or relations, and not edge labels.
          if '🏷' in cur[k]:
            label= vl(cur,[k,'🏷']).replace('\\\\n',' ') #version of label for single line text
            labelr= vl(cur,[k,'🏷']).replace('\\\\n','\\n') #version of label for GV w/ return
          else:
            label= ''
          nlb_txt.SetValue(label)
          nt=k.split('🔸')[0]
          #node type is the first atom
          id=k.split('🔸')[1]
          #id is the second atom
          if nt=='⚗️':
            dat_grd.SetCellValue(i,0,id+': '+label)
            #set left row label
            if k=='⚗️🔸'+nav['proc']['s']:
              #mark highlighted row 
              dat_grd.SetCellTextColour(i,0,"white")
              dat_grd.SetCellBackgroundColour(i,0,colr['magenta'])
              if '🗨️' in cur[k]:
                cmt_txt.SetValue(vl(cur,['🗨️']))
              else:
                cmt_txt.SetValue('')
            else:
              dat_grd.SetCellTextColour(i,0,"black")
              dat_grd.SetCellBackgroundColour(i,0,colr_lighter['magenta'])
            dat_grd.SetCellValue(i,2,id+": "+label)
            #set right row label
            dat_grd.SetCellBackgroundColour(i,2,colr_lighter['magenta'])
            for p in cur['⚗️🔸'+nav['proc']['s']]:
              if p in predicates:
                for so in cur['⚗️🔸'+nav['proc']['s']][p]:
                #search through predicates in selected process
                  if so==k:
                    #Is the right pane connected to the left?  If so, set the predicate
                    dat_grd.SetCellValue(i,1,p)
            for p in cur[k]:
              if p in predicates:
                for o in cur[k][p]:
                  if o not in properties:
                    #search through nodes connected to current node
                    if o=='⚗️🔸'+nav['proc']['s']: #is focus nav['proc']['s'] connected to by the current node?
                      if p=='➡️':
                        dat_grd.SetCellValue(j,1,'⬅️')
                      elif p=='⬅️':
                        dat_grd.SetCellValue(j,1,'➡️')
                      else:
                        dat_grd.SetCellValue(j,1,'↔️')
                    G[pstr].add_edge(k,o,dir=efo(p))
            if '🔸'.join(path)+'🔸'+id in full:
            #Is the process a zoom to next level?
              G[pstr].add_node(k,href='nav.html#'+pstr+'🔸'+k+'.svg',color=colr['magenta'],
                penwidth=5, label='{<f0> '+k.split('🔸')[1]+'|<f1> '+labelr+'\n\n\n}',shape='Mrecord')
            else:
              G[pstr].add_node(k,color=colr['magenta'], penwidth=3, 
                label='{<f0> '+k.split('🔸')[1]+'|<f1> '+labelr+'\n\n\n}',shape='Mrecord')

            i+=1
            j+=1
            typ=''
          elif nt=='💽':
            dat_grd.SetCellBackgroundColour(j,2,colr_lighter['orange'])
            G[pstr].add_node(k,color=colr['orange'], penwidth=3,label='<f0> D'+k.split('🔸')[1]+'|<f1> '+labelr+'',shape='record')
            dat_grd.SetCellValue(j,2,'D'+id+": "+label)
          elif nt=='👤':
            dat_grd.SetCellBackgroundColour(j,2,colr_lighter['cyan'])
            G[pstr].add_node(k,color=colr['cyan'], penwidth=3, 
            label=labelr,shape='record')
            dat_grd.SetCellValue(j,2,label)
          if nt=='💽' or nt=='👤':
            for p in cur['⚗️🔸'+nav['proc']['s']]:
              if p in predicates:
                for so in cur['⚗️🔸'+nav['proc']['s']][p]:
                  if so==k:
                    dat_grd.SetCellValue(j,1,p)
            j+=1
      options='-Epenwidth=2 -Npenwidth=2 -Nfontname="sans-serif" -Gsize="13,9" -Gmargin=".25" -Goverlap="prism"' 
      options+=' -Ecolor="#888888" -Gsplines=true -Gsep="+5"'
      return G[pstr].draw(None,format='svg',prog='neato',args=options)

    def page_loaded(event):
      page=urllib.parse.unquote(event.GetURL())
      if page!='about:blank': 
        nav['func']['s']='✨ page_loaded'
        if nav['wclck']['s']:
          if page.find('.svg')!=-1:
            nav['proc']['s']='1'
            nav['level']['s']=page[page.rfind('#')+1:].replace('⚗️🔸','').replace('.svg','').split('🔸') 
            nav['ldnav']['s']=True
            nav_web.SetPage(create_nav(nav['level']['s']),base)
        if nav['ldnav']['s']:
          nav['ldnav']['s']=False
          nav['ldsvg']['s']=True
          svg=refresh(nav['level']['s']).decode('utf-8')
          gra_web.SetPage(svg,base)
        if nav['ldsvg']['s']:
          nav['ldsvg']['s']=False
          nav['wclck']['s']=True

    def dat_dclick(event):
      nav['func']['s']='✨ dat_dclick'
      six=9
      
    def dat_click(event):
      nav['func']['s']='✨ dat_click'
      row=event.GetRow()
      col=event.GetCol()
      cval=dat_grd.GetCellValue (row,col)
      ldct=pydash.objects.get(full,'🔸'.join(nav['level']['s']))
      if col==1:
        res=[]
        #✨⛔️
        for k in ldct:
          if k not in (properties + predicates) and k.count('🔸')==1:
            res.append(k)
        if dat_grd.GetCellValue (row,col)=='':
          dat_grd.SetCellValue(row,col,'↔️')
          pydash.objects.set_(ldct,['⚗️🔸'+nav['proc']['s'],'↔️',res[row]],{})
          mess=base64.b64encode(bytearray('🔸'.join(nav['level']['s'])+'▪️⚗️🔸'+nav['proc']['s']+'🔹↔️🔹'+res[row],"utf8")).decode('utf-8')
          h = SHA256.new(bytearray(mess,"utf8"))
          signature = base64.b64encode(pkcs1_15.new(priv).sign(h)).decode('utf-8')
          publish.single('all',hname+'🔹✨🔹'+mess+'🔸'+signature)
        elif dat_grd.GetCellValue (row,col)=='↔️':
          dat_grd.SetCellValue(row,col,'⬅️')
          if pydash.objects.has(ldct,['⚗️🔸'+nav['proc']['s'],'↔️',res[row]]):  
            del ldct['⚗️🔸'+nav['proc']['s']]['↔️'][res[row]]  
          if pydash.objects.has(ldct,[res[row],'↔️','⚗️🔸'+nav['proc']['s']]):  
            del ldct[res[row]]['↔️']['⚗️🔸'+nav['proc']['s']]  
          pydash.objects.set_(ldct,['⚗️🔸'+nav['proc']['s'],'⬅️',res[row]],{})
          messd=base64.b64encode(bytearray('🔸'.join(nav['level']['s'])+'▪️⚗️🔸'+nav['proc']['s']+'🔹↔️🔹'+res[row],"utf8")).decode('utf-8')
          h = SHA256.new(bytearray(messd,"utf8"))
          signature = base64.b64encode(pkcs1_15.new(priv).sign(h)).decode('utf-8')
          publish.single('all',hname+'🔹⛔️🔹'+messd+'🔸'+signature)
          mess=base64.b64encode(bytearray('🔸'.join(nav['level']['s'])+'▪️⚗️🔸'+nav['proc']['s']+'🔹⬅️🔹'+res[row],"utf8")).decode('utf-8')
          h = SHA256.new(bytearray(mess,"utf8"))
          signature = base64.b64encode(pkcs1_15.new(priv).sign(h)).decode('utf-8')
          publish.single('all',hname+'🔹✨🔹'+mess+'🔸'+signature)
        elif dat_grd.GetCellValue (row,col)=='⬅️':
          dat_grd.SetCellValue(row,col,'➡️')
          if pydash.objects.has(ldct,['⚗️🔸'+nav['proc']['s'],'⬅️',res[row]]):  
            del ldct['⚗️🔸'+nav['proc']['s']]['⬅️'][res[row]]  
          if pydash.objects.has(ldct,[res[row],'➡️','⚗️🔸'+nav['proc']['s']]):  
            del ldct[res[row]]['➡️']['⚗️🔸'+nav['proc']['s']]  
          pydash.objects.set_(ldct,['⚗️🔸'+nav['proc']['s'],'➡️',res[row]],{})
          messd=base64.b64encode(bytearray('🔸'.join(nav['level']['s'])+'▪️⚗️🔸'+nav['proc']['s']+'🔹⬅️🔹'+res[row],"utf8")).decode('utf-8')
          h = SHA256.new(bytearray(messd,"utf8"))
          signature = base64.b64encode(pkcs1_15.new(priv).sign(h)).decode('utf-8')
          publish.single('all',hname+'🔹⛔️🔹'+messd+'🔸'+signature)
          mess=base64.b64encode(bytearray('🔸'.join(nav['level']['s'])+'▪️⚗️🔸'+nav['proc']['s']+'🔹➡️🔹'+res[row],"utf8")).decode('utf-8')
          h = SHA256.new(bytearray(mess,"utf8"))
          signature = base64.b64encode(pkcs1_15.new(priv).sign(h)).decode('utf-8')
          publish.single('all',hname+'🔹✨🔹'+mess+'🔸'+signature)
        elif dat_grd.GetCellValue (row,col)=='➡️':
          dat_grd.SetCellValue(row,col,'')
          if pydash.objects.has(ldct,['⚗️🔸'+nav['proc']['s'],'➡️',res[row]]):  
            del ldct['⚗️🔸'+nav['proc']['s']]['➡️'][res[row]]  
          if pydash.objects.has(ldct,[res[row],'⬅️','⚗️🔸'+nav['proc']['s']]):  
            del ldct[res[row]]['⬅️']['⚗️🔸'+nav['proc']['s']]  
          messd=base64.b64encode(bytearray('🔸'.join(nav['level']['s'])+'▪️⚗️🔸'+nav['proc']['s']+'🔹➡️🔹'+res[row],"utf8")).decode('utf-8')
          h = SHA256.new(bytearray(messd,"utf8"))
          signature = base64.b64encode(pkcs1_15.new(priv).sign(h)).decode('utf-8')
          publish.single('all',hname+'🔹⛔️🔹'+messd+'🔸'+signature)
        svg=refresh(nav['level']['s']).decode('utf-8')
        gra_web.SetPage(svg,'/')
        event.Skip()
      if col==0:
        nav['proc']['s']=cval[:cval.find(':')]
        svg=refresh(nav['level']['s']).decode('utf-8')
        gra_web.SetPage(svg,'/')
      event.Skip()
    dat_grd.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, dat_dclick)
    dat_grd.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, dat_click)
    gra_web.Bind(wx.html2.EVT_WEBVIEW_LOADED, page_loaded)
    nav_web.Bind(wx.html2.EVT_WEBVIEW_LOADED, page_loaded)

class Gedit(wx.App):
  def OnInit(self):
    self.frame = edt_frm()
    self.SetTopWindow(self.frame)
    self.frame.Show()
    return True
if __name__ == '__main__':
  app = Gedit()
  app.MainLoop()
