# This code demonstrates how to modify data flows between entities, data stores, and processes
# for Gane and Sarson notation, replacing node shapes with colored emoji cards.  
from dash import Dash, html,Input,Output,dash_table,dcc,ctx,no_update
import dash_interactive_graphviz,re
from grapheme import graphemes as a #a=atoms
from natsort import natsorted
import networkx as nx

app = Dash(__name__)

dot_header='''
digraph {
node [shape = "plain"]
node [fontname = "Helvetica-Bold"]
edge [fontname = "Helvetica-Bold"]
graph [fontname = "Helvetica-Bold"]
bgcolor=transparent
charset="utf-8"
splines="true"
'''

c={
  '👤':'#33BBEE',
  '👤📐':' COLOR="#33BBEE" ',
  '👤☄️':'#e4fcff',
  '💽':'#EE7733',
  '💽📐':' COLOR="#EE7733" ',
  '💽☄️':'#ffd6bc',
  '⚗️':'#EE3377',
  '⚗️📐':' COLOR="#EE3377" ',
  '⚗️☄️':'#fcf1f5',
  '⚫':'#000000',
  '⚫📐':' COLOR="#000000" ',
}
# palette for color blindness from https://personal.sron.nl/~pault/

def gs_node_label(nid,label):
  l=''
  for line in label.split('\\\\n'):
    if l=='':
    # Start new label
      node_class,node_num=nid.split('🔸')
      # split node id into class and number
      if node_class=='💽':
        l+='<FONT '+c['⚫📐']+' POINT-SIZE="16" ><B>[D'+node_num+']</B></FONT><BR />'
      else:
        l+='<FONT '+c['⚫📐']+' POINT-SIZE="16" ><B>['+node_num+']</B></FONT><BR />'
      l+='<FONT POINT-SIZE="4" > </FONT><BR />'
    l+='<FONT  '+c['⚫📐']+' POINT-SIZE="16" ><B>'+line+'</B></FONT><BR />'
  gv_label='"'+node_class+'🔸'+node_num+'" [label=< <TABLE '+c[node_class+'📐']+\
    'BORDER="4"><TR><TD BORDER="0" CELLPADDING="6"><FONT POINT-SIZE="44" >'
  gv_label+=node_class+'</FONT></TD><TD BORDER="0">'+l+'</TD><TD BORDER="0">      </TD></TR></TABLE> >];\n'
  return(gv_label)

G={}

predicates=list(a('➡️⬅️↔️'))
# Emoji for direction of data flow.


with open('triples.txt') as tr:
  for lt in tr.readlines():
    line=lt.strip()
    level,s,p,o=re.split(r'▪️|🔹',line)
    if not level in G:
      G[level]=nx.MultiDiGraph()
    if p=='🏷':
      G[level].add_node(s,label=o)
    if p=="➡️":
      G[level].add_edge(s,o)
    if p=="⬅️":
      G[level].add_edge(o,s)
    if p=="↔️":
      G[level].add_edge(s,o)
      G[level].add_edge(o,s)

def update_level(level,curr_proc):
  sub_rows={}
  obj_rows={}
  gv_nodes={}
  gv_edges={}
  for node in G[level].nodes(data='label'):
    gv_nodes[node[0]]=gs_node_label(node[0],node[1])
    if curr_proc and node[0]!=curr_proc:
      if G[level].has_edge(curr_proc,node[0]) and G[level].has_edge(node[0],curr_proc):
        row={'s':node[0],'p':'↔️','o':node[0]}
      elif G[level].has_edge(curr_proc,node[0]):
        row={'s':node[0],'p':'➡️','o':node[0]}
      elif G[level].has_edge(node[0],curr_proc):
        row={'s':node[0],'p':'⬅️','o':node[0]}
      else:
        row={'s':node[0],'p':'','o':node[0]}
    else:
      row={'s':node[0],'p':'','o':node[0]}
    if node[0].find('⚗️')!=-1:
      sub_rows[node[0]+'🔹'+node[0]]=row
    else:
      obj_rows[node[0]]={'s':'','p':row['p'],'o':row['o']}
  for edge in G[level].edges:
    if G[level].has_edge(edge[1],edge[0]) and G[level].has_edge(edge[0],edge[1]):
      gv_edges[edge[0]+'🔹'+'-'+'🔹'+edge[1]]=\
        '"'+edge[0]+'" -> "'+edge[1]+'" [dir=both penwidth="4"]'
    elif G[level].has_edge(edge[0],edge[1]):
      gv_edges[edge[0]+'🔹'+'-'+'🔹'+edge[1]]=\
        '"'+edge[0]+'" -> "'+edge[1]+'" [dir=forward penwidth="4"]'
    elif G[level].has_edge(edge[1],edge[0]):
      gv_edges[edge[0]+'🔹'+'-'+'🔹'+edge[1]]=\
        '"'+edge[0]+'" -> "'+edge[1]+'" [dir=back penwidth="4"]'
  return(
    [dot_header+'\n'.join(gv_nodes.values())+'\n'+'\n'.join(gv_edges.values())+'}',
    natsorted(sub_rows.values(),key=lambda row: row['s'])+
    natsorted(obj_rows.values(),key=lambda row: row['o'])]
  )

app.layout = html.Div(
  [
    html.Div(
      [
        html.Div(
          [
            html.Div(
              dcc.Dropdown(
                id='level',
                options=[{'label':i, 'value': i} for i in natsorted(G.keys())]
              ),
            ),
            html.Div(
              dcc.Textarea(
                rows=1,
                id='curr_proc',
                value='',
              ),
            ),
            html.Div(
              dcc.Checklist(
                ['Auto Graph'],
                ['Auto Graph'],
                id='auto_graph',
              ),
            ),
          ],
          className='topbar'
          #style={'display':'flex','justifyContent':'space-between'}
        ),
        dash_table.DataTable(
          id='dataflow',
          sort_action="native",
          filter_action="native",
          columns=[
            {'id':'s','name':'s'},
            {'id':'p','name':'p'},
            {'id':'o','name':'o'}
          ],
          data=None,
          style_data_conditional=[
            # some people track color vs. symbols, so use all means.
            {'if': {'column_id':['s','o'],'filter_query':'{s} contains "⚗️" or {o} contains "⚗️"'}
              ,'backgroundColor': c['⚗️☄️']},
            {'if': {'column_id':['s','o'],'filter_query':'{s} contains "💽" or {o} contains "💽"'}
              ,'backgroundColor': c['💽☄️']},
            {'if': {'column_id':['s','o'],'filter_query':'{s} contains "👤" or {o} contains "👤"'}
              ,'backgroundColor': c['👤☄️']},
          ],
        ),
      ],
      style={'display':'flex','flex-direction':'column'},
    ),
    html.Div(
      dash_interactive_graphviz.DashInteractiveGraphviz(
        id="gv",
        engine="fdp",
        fit_button_content="🔄",
        dot_source='digraph {}'
      ),
      style={"flexGrow":"1","position":"relative"}
   )
  ],
  style={"position":"absolute","height":"100%","width":"99vw","display":"flex"}
)

@app.callback(
  Output('gv','dot_source'),
  Output('dataflow', 'data'),
  Output('dataflow', 'active_cell'),
  Output('gv', 'selected_node'),
  Output('gv', 'selected_edge'),
  Output('level', 'value'),
  Output('curr_proc', 'value'),
  Input('dataflow', 'active_cell'),
  Input('level','value'),
  Input('gv', 'selected_node'),
  Input('dataflow', 'data'),
  Input('curr_proc', 'value'),
  Input('auto_graph', 'value')
)

def change_grid(ccell,level,node,dataflow,cp,ag):
  if level:
    if ctx.triggered_id=='auto_graph' and len(ag)>0:
      cur=update_level(level,None)
      return ( cur[0], no_update, no_update, no_update, no_update, no_update, no_update,)
    if ctx.triggered_id=='level':
      cur=update_level(level,None)
      return ( cur[0], cur[1], None, None, None, level, '')
    if ctx.triggered_id=='gv':
      if node:
        num=node.split('🔸')[1]
        nest='🔸'+num
        if level+nest not in G:
          nest=''
        else:
          cur=update_level(level+nest,None)
          return ( cur[0], cur[1], None, None, None, level+nest, None)
    if ctx.triggered_id=='dataflow':
      if ccell:
        if ccell['column']==0:
          c_sub=dataflow[ccell['row']]['s']
          cur=update_level(level,c_sub)
          return (cur[0],cur[1],None,None,None,level,c_sub)
        elif ccell['column']==1:
          if cp:
            sel_pred=dataflow[ccell['row']]['o']
            if not (G[level].has_edge(cp,sel_pred) or G[level].has_edge(sel_pred,cp)):
              G[level].add_edge(cp,sel_pred)
              G[level].add_edge(sel_pred,cp)
            elif (G[level].has_edge(cp,sel_pred) and G[level].has_edge(sel_pred,cp)):
              G[level].remove_edge(sel_pred,cp)
            elif G[level].has_edge(cp,sel_pred):
              G[level].add_edge(sel_pred,cp)
              G[level].remove_edge(cp,sel_pred)
            elif G[level].has_edge(sel_pred,cp):
              G[level].remove_edge(sel_pred,cp)
            cur=update_level(level,cp)
            if len(ag)>0: return (cur[0],cur[1],None,None,None,level,cp)
            else:
              return ( no_update, cur[1], None, None, None, level, cp)
  return no_update
if __name__ == '__main__':
    app.run_server(debug=True)
