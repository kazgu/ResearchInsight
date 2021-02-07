import json
import matplotlib.pyplot as plt
import numpy as np
import json
from pyecharts import options as opts
from pyecharts.charts import Graph
import urllib.request
import pandas as pd

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
    def trends(self):
        trends={}
        for index,row in self.data.iterrows():
            if row['year'] not in trends:
                trends[row['year']]=1
            else:
                trends[row['year']]+=1
        fig, axes = plt.subplots(1, 1, figsize=(15, 8))
        x ,y=[k for k in trends ][:10],[trends[k] for k in trends ][:10]
        plt.plot(x, y)
        plt.show()
    def Search(self,keyword):
        result=[ff for ff in  self.data['title'] if keyword.lower() in ff.lower() ]
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
                item['draggable']="False"
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
                addnode(au,1,8,len(nodes)+1,"author","True",False,True)
            ######### title
            addnode(row['title'],1,5,len(nodes)+1,"paper","False",False,True)
            ######### venue
            addnode(row['venue'],1,2,len(nodes)+1,"venue","True",False,True)
            ######### type
            addnode(row['type'],1,0.5,len(nodes)+1,"type","True",False,True)
            ######### year
            addnode('%s'%row['year'],1,1,len(nodes)+1,"year","True",False,True)
            
            ################################ relation
            for au in row['authors'].split(','):
                item={}
                item['source']=row['title']
                item['target']=au
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
        catogories=[{"name":ct} for ct in  set([nd['category'] for nd in nodes])]
        c = (
        Graph()
        .add(
            "",
            nodes,
            relation,
            catogories,
            repulsion=50,
            linestyle_opts=opts.LineStyleOpts(curve=0.2),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            legend_opts=opts.LegendOpts(is_show=False),
            title_opts=opts.TitleOpts(title="Graph"),
        )
        .render("%s.html"%self.name)
    )