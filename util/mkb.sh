#pandoc -N --toc  -fmarkdown-implicit_figures --toc-depth=6 --template="../templates/template.html" -t html5 -s -o ../index.html ../README.md
pandoc -N --toc --toc-depth=6 --template="../templates/template.html" -t html5 -s -o ../index.html ../README.md
perl -pi -e "s|<br />|<br>|g" ../index.html
#perl -0777 -pi -e 's|<img\s+src=|<img loading="lazy" src=|g' ../index.html
