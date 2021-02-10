import json
import matplotlib.pyplot as plt
import numpy as np
import json
from pyecharts import options as opts
from pyecharts.charts import Graph
import urllib.request
import pandas as pd
import os

class ResearchInsight():
    def __init__(self,name):
        self.name=name
        self.data=None
        self.readData()
    def readData(self):
        vv={}
        vv['q']=self.name
        vvv=urllib.parse.urlencode(vv)
        url='https://dblp.org/search/publ/api?%s&h=2000&format=json'%(vvv)
        data2 = urllib.request.urlopen(url).read()
        data=json.loads(data2,encoding="utf-8")
        data=data['result']['hits']['hit']
        pdata=[]
        dist={}
        for i, d in enumerate(data):
            try:
                if d['info']['title'].lower() not in dist:
                    dist[d['info']['title'].lower()]=1
                else:
                    continue
                ats=d['info']['authors']['author']
                authors= ','.join([a['text'] for a in  ats ]) if type(ats) is list else ats['text']
                item={}
                item['authors']=authors
                item['title']=d['info']['title']
                item['venue']=d['info']['venue']
                item['type']=d['info']['type']
                item['url']=d['info']['ee']
                item['year']=int(d['info']['year'])
                pdata.append(item)
            except:
                pass
        fdata=pd.DataFrame(pdata)
        fdata.sort_values(by=["year"],ascending=[False],inplace=True)
        self.data=fdata
        print(30*'*','info',30*'*')
        print('paper count:%s'%(len(set([fd for fd in fdata['title']  ]))))
        print('authors count:%s'%(len(set([af for fd in fdata['authors'] for af in fd.split(',') ]))))
        print('venue count:%s'%(len(set([af for fd in fdata['venue']  for af in fd ]))))
        print('published years:%s'%(set([fd for fd in fdata['year'] ])))
    def trends(self,top=10):
        trends={}
        for index,row in self.data.iterrows():
            if row['year'] not in trends:
                trends[row['year']]=1
            else:
                trends[row['year']]+=1
        fig, axes = plt.subplots(1, 1, figsize=(15, 8))
        x ,y=[k for k in trends ][:top],[trends[k] for k in trends ][:top]
        plt.plot(x, y)
        plt.savefig("%s.jpg"%self.name)
        plt.show()
    def Search(self,keyword):
        result=[[ff,yy] for ff,yy in  zip(self.data['title'],self.data['year']) if keyword.lower() in ff.lower() ]
        return len(result),result
    def ExportReadList(self,year=0):
        pc=0
        ttD={}
        with open('readlist.html','w',encoding='utf-8') as f:
            f.write('<html><head></head><body>\n')
            for index,row in self.data.iterrows():
                if row['year']>year:
                    f.write('<p><h3><a href={0} target="_blank">{1}:{2}</a><h3><p>\n'.format(row['url'],row['year'],row['title']))
            f.write('<body></html>')
    def toGraph(self):
        nodes=[]
        relation=[]
        catogories=[]
        node_dict={}
        def addnode(name,ssize,sdis,value,category,show,isShowLabel=True,isaddSize=True):
            try:
                item={}
                if type(name) is list:
                    name=name[0]
                item['name']=name
                item['symbolSize']=ssize
                item['draggable']="True"
                item['value']=value
                item['category']=category
                if isShowLabel:
                    item['label']={}
                    item['label']['normal']={}
                    item['label']['normal']['show']=show
                if name not in node_dict:
                    node_dict[name]=item
                else:
                    if isaddSize:
                        node_dict[name]['symbolSize']+=sdis
            except:
                print(name)
        for index,row in self.data.iterrows():
            ########################## nodes
            ######### authors
            for au in row['authors'].split(','):
                addnode(au,5,8,len(nodes)+1,"author","True",False,True)
            ######### title
            addnode(row['title'],1,1,len(nodes)+1,"paper","False",False,True)
            ######### venue
            addnode(row['venue'],3,2,len(nodes)+1,"venue","True",False,True)
            ######### type
            addnode(row['type'],3,0.5,len(nodes)+1,"type","True",False,True)
            ######### year
            addnode('%s'%row['year'],3,1,len(nodes)+1,"year","True",False,True)
            
            ################################ relation
            for au in row['authors'].split(','):
                item={}
                item['source']=row['title']
                item['target']=au
                node_dict[row['title']]['symbolSize']+=int(node_dict[au]['symbolSize']/3)
                relation.append(item)
                
            item={}
            item['source']=row['title']
            item['target']=row['venue']
            relation.append(item)

            item={}
            item['source']=row['title']
            item['target']=row['type']
            relation.append(item)

            item={}
            item['source']=row['title']
            item['target']='%s'%row['year']
            relation.append(item)
            
        ############################################ catagorie
        nodes=[node_dict[k] for k in node_dict]
        ndata=pd.DataFrame(nodes)
        ndata.sort_values(by=["symbolSize"],ascending=[False],inplace=True)
        catogories=[{"name":ct} for ct in  set([nd['category'] for nd in nodes])]
        c = (
        Graph()
        .add(
            "",
            nodes,
            relation,
            catogories,
            repulsion=100,
            linestyle_opts=opts.LineStyleOpts(curve=0.2),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            legend_opts=opts.LegendOpts(is_show=False),
            title_opts=opts.TitleOpts(title="Graph"),
        )
        .render("%s.html"%self.name)
    )
        fname="%s.html"%self.name
        topa=[row['name'] for index,row in  ndata.iterrows()  if row['category']=='author']
        author_dict={}
        for i,row in self.data.iterrows():
            for a in row['authors'].split(','):
                if a not in author_dict:
                    author_dict[a]=[row]
                else:
                    author_dict[a].append(row)
        strtop='\n'.join(['<li style="background:rgb(237,68,17,%s)">%s</li>'%(1-i*0.06,t) for i,t in enumerate(topa[:15])])
        rdata=[aa for a in topa[:15] for aa in author_dict[a]]
        readlist='\n'.join(['<li><h4><a href={0} target="_blank">[{4}]{1},<span style="color:rgb(237,68,17)" >{2}</span>;({3})</a><h4></li>'.format(row['url'],row['authors'],row['title'],row['year'],i) for i, row in enumerate(rdata)])
        readlist='<div><ul>%s</ul></div>'%readlist
        with open(fname,'r',encoding='utf8') as f:
            lines=f.readlines()
            for i in range(len(lines)):
                if 'style="width:900px; height:500px;"' in lines[i]:
                    lines[i]=lines[i].replace('style="width:900px; height:500px;"','style="width:100%; height:600px;"')
            if os.path.exists("%s.jpg"%self.name):
                for i in range(len(lines)):
                    if '></div>' in lines[i]:
                        lines[i]=lines[i].replace('></div>','></div>\n<table border="0" style="width:{0}"><tr><td style="width:{2}"><img src="{1}" width="{0}"/></td><td style="width:{3}"><ul>{4}</ul></td></tr></table>{5}'.format('100%',"%s.jpg"%self.name,'70%','30%',strtop,readlist))
                
            with open(fname,'w',encoding='utf8') as ww:
                for line in lines:
                    ww.write(line)

            
    def to_all(self):
        self.trends(20)
        self.toGraph()
        