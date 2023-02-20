# coding=utf-8
from datetime import date,datetime
import os

tss=date.isoformat(datetime.now())
os.system('cat ../README.md > ../interim/all.md')
os.system('date +%Y-%m-%d | perl -pi -e "s|datehere|'+tss+'|g" ../interim/all.md')
ts=datetime.utcnow().isoformat(sep='T', timespec='milliseconds').replace(':','').replace('-','').replace(' ','')+'Z'
os.system('pandoc -N --toc  -fmarkdown-implicit_figures --toc-depth=6 --template="../templates/template.html" -t html5 -s -o ../index.html ../interim/all.md')
os.system('perl -pi -e "s|<br />|<br>|g" ../index.html')
os.system('rm ../interim/all.md')
