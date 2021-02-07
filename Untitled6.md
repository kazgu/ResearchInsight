```python
from ResearchInsight import ResearchInsight
```


```python
res=ResearchInsight('knowledge graph completion')
```

    ****************************** info ******************************
    paper count:140
    authors count:509
    venue count:52
    published years:{2016, 2017, 2018, 2019, 2020, 2021, 2015}
    


```python
res.trends()
```


![png](output_2_0.png)



```python
res.Search('survey')
```




    (2,
     ['Survey and Open Problems in Privacy Preserving Knowledge Graph - Merging, Query, Representation, Completion and Applications.',
      'A Survey on Graph Neural Networks for Knowledge Graph Completion.'])




```python
res.toGraph()
```


```python

```
