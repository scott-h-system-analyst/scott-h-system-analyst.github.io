# coding=utf-8
# Dash and modules via pip on 2023-02-20
from dash import Dash, html,Input,Output
import dash_mqtt,dash_interactive_graphviz
app = Dash(__name__)
dot_header='''
digraph {
node [shape = "plain"];
node [fontname = "Helvetica-Bold"];
edge [fontname = "Helvetica-Bold"];
graph [fontname = "Helvetica-Bold"];
bgcolor=transparent;
charset="utf-8";
splines="true";
'''
def color_box(u_char):
  #palette for color blindness from https://personal.sron.nl/~pault/
  if u_char=='👤':
    return ' COLOR="#33BBEE" '
  elif u_char=='💽':
    return ' COLOR="#EE7733" '
  elif u_char=='⚗️':
    return ' COLOR="#EE3377" '
  else:
    return ''
def dir_arrow(u_char):
  if u_char=='➡️':
    return ' dir="forward" '
  elif u_char=='⬅️':
    return ' dir="back" '
  elif u_char=='↔️':
    return ' dir="both" '
  else:
    return ' dir="none" '
labels={}
edges={}
nodes={}
app.layout = html.Div([
  dash_mqtt.DashMqtt(
    id='mqtt',
    broker_url='192.168.52.51',
    #for some reason localhost doesn't work with this module
    #MQTT broker needs WebSockets capability ('protocol websockets' in mosquitto.conf)
    broker_port = 9001,
    broker_path = 'mqtt',
    topics=['all']
  ),  
  html.Div(
    dash_interactive_graphviz.DashInteractiveGraphviz(id="gv",engine="fdp")
  )
])
@app.callback(
  Output('gv','dot_source'),
  Input('mqtt','incoming')
)
def update_triples(msg):
  if msg:
    tr='\n'
    tri=msg['payload'].split('🔹')
    if tri[1]=='🏷':
      labels[tri[0]]=tri[2]
    else:
      for k in [tri[0],tri[2]]:
        l=''
        for line in labels[k].split('\\n'):
          if l=='':
            i,j=k.split('🔸')
            if i=='💽':
              l+='<FONT COLOR="#123456" POINT-SIZE="16" ><B>[D'+j+']</B></FONT><BR />'
            else:
              l+='<FONT COLOR="#123456" POINT-SIZE="16" ><B>['+j+']</B></FONT><BR />'
            l+='<FONT POINT-SIZE="4" > </FONT><BR />'
          l+='<FONT COLOR="#123456" POINT-SIZE="16" ><B>'+line+'</B></FONT><BR />'
        tr+='"'+i+'🔸'+j+'" [label=< <TABLE '+color_box(i)+'BORDER="4"><TR><TD BORDER="0" CELLPADDING="6"><FONT POINT-SIZE="44" >'+i+'</FONT></TD><TD BORDER="0">'+l+'</TD><TD BORDER="0">      </TD></TR></TABLE> >];\n'
        nodes[k]=tr
      edges[msg['payload']]='"'+tri[0]+'"->"'+tri[2]+'" [fontcolor="#123456" color="#123456" penwidth=3'+dir_arrow(tri[1])+']\n'
    return dot_header+'\n'.join(nodes.values())+'\n'+'\n'.join(edges.values())+'}'
if __name__ == '__main__':
    app.run_server(debug=True)
