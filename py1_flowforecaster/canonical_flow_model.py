# -*- coding: utf-8 -*-
"""Canonical Flow Model (in development).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1YCO7Pp-65bFyr3jQGmtB6HpAfuykXdBE

### Rules for Data Flow Lifecycles
#### Scaling rules:
- R1: producer/consumer divides a varying data set by a fixed number of tasks, causing the operation size to scale
- R2: producer/consumer takes a replica of a data set (for ensemble)
- R3: producer/consumer takes fixed-size chunking causing tasks or operations to scale

#### Non-scaling rules (sequential, non parallel):
- R4: producer/consumer takes the same data apart and remain constant across varying tasks or data set (independent zone)
- R5: producer/consumer takes chunks of a variable size dependent only to data set
- R6: producer/consumer finds a boundary of folding caterpillars by traversing a same group of vertices at the current depth (in level-wise).


### Remainder policy
- RP1: indirect data retrieval from producer/consumer should be added to the calculation of data flow
  (use case: FASTQ downloads SRA data by identifier from SRA Search)
- RP2: cascade for efficiency; employs larger producer/consumer for critical data flow and then takes smaller one for less priortized.

### Coverage
- edge counts (rule-applied edges/total edges)

### Available metrics
- access size (average, max, std)
- operation count

### Default set of DFL data
- n tasks (1x, 2x, 4x)
- data set sizes (1x, 4x, 9x)

### User custom API
- manual statistics (TBD)
"""



"""Workflow Summary

| Workflow    | Rules | Remainder policy | Folding | Data point | Metric |
| -------- | ------- | ------- | ------- | ------- | ---- |
| 1000 Genomes  | R2, R3, R4, R6 | n/a | horizontal (spatial) | 1x, 4x, 9x input size<br> 1x, 2x, 4x task count | volume, (access in average, max, std) |
| Montage  | R1, R3, R5    | n/a | | 1x, 4x, 9x input size<br> 1x, 2x, 4x task count | volume, (access in average, max, std) |
| DeepDriveMD  | R2, R3, R4, R6 | n/a | vertical (temporal) | 1x, 4x, 9x input size<br> 1x, 2x, 4x task count | volume, (access in average, max, std) |
| SRA Search  | R3, R5 | RP1 | | 1x, 4x, 9x input size<br> 1x, 2x, 4x task count | volume, (access in average, max, std) |

### Equation

\begin{equation}
  Volume_{fanout\_normal\_scaling~~} (data_u,task_v) =
  \begin{array}{cl}
  \frac{n_u}{d_u},  \forall v \in N(u)
  \end{array}~~ [eq. 1]
  \end{equation}

\begin{equation}
Volume_{fanout\_fixed\_vol\_xfer~~} (data_u,task_v) =
\begin{array}{cl}
n_u,  \forall v \in N(u)
\end{array}~~ [eq. 2]
\end{equation}

\begin{equation}
Volume_{fanin\_dv\_gt\_one~~}(data_u,task_v) =
\begin{array}{cl}
\frac{n_v}{d_v},  \forall u \in N(v)
\end{array}~~ [eq. 3]
\end{equation}

\begin{equation}
Volume_{fanin\_dv\_eq\_one\_sequential~~}(data_u,task_v) =
\begin{array}{cl}
n_v,  \forall u \in N(v)
\end{array}~~ [eq. 4]
\end{equation}

\begin{equation}
Volume_{fanout\_normal\_scaling\_with\_access\_size~~} (data_u,task_v) =
\begin{array}{cl}
\frac{n_u}{d_u} * Total\_Frequency,  \forall v \in N(u)
\end{array}~~ [eq. 5]
\end{equation}


\begin{equation}
  Volume_{fanout\_normal\_scaling~~} (data_u,task_v) =
  \begin{array}{cl}
  \frac{block\_size * total\_access\_count}{d_u},  \forall v \in N(u)
  \end{array}~~ [eq. 1]
  \end{equation}

 \begin{equation}
  Volume_{fanout\_normal\_scaling~~} (data_u,task_v) =
  \begin{array}{cl}
  \frac{total\_num\_blocks * avg\_block\_size  * avg\_access\_freq}{d_u},  \forall v \in N(u)
  \end{array}~~ [eq. 1]
  \end{equation}


- **$u, v \in N$**: u and v are a pair of nodes (vertices)
- **$d_u$**: out-degree of vertex u
- **$d_v$**: in-degree of vertex v
- **$n_u$**: data size from vertex u
- **$n_v$**: aggregated data size to vertex v
- **$N()$**: a set of all neighbor vertices of a $vertex$

# Rate (volume / operation count)

Rate (to request data transfer) doesn’t change by # of processors and the current observations are so far:
- varying by # of tasks doesn’t change rate, it’s contant
- vary by tasks (e.g., 10000 genomes have individuals: 8k, frequency: 19k)
- vary by input size (Montage is smart to increase access size for larger input data)
- doesn’t vary by edge type (fan-in, fan-out)

Example of 1000 Genomes' individuals task

- 4 tasks:

  ```
    ALL.chr1.250000.vcf individuals_ID0000001 {'weight': 8191.990951754038}
    ALL.chr1.250000.vcf individuals_ID0000002 {'weight': 8191.990951754038}
    ALL.chr1.250000.vcf individuals_ID0000003 {'weight': 8191.990951754038}
    ALL.chr1.250000.vcf individuals_ID0000004 {'weight': 8191.990951754038}
  ```

- 2 tasks:

  ```   
    ALL.chr1.250000.vcf individuals_ID0000001 {'weight': 8191.990951754038}
    ALL.chr1.250000.vcf individuals_ID0000002 {'weight': 8191.990951754038}
  ```
"""

import networkx as nx
import numpy as np
from matplotlib import pyplot as plt
from pprint import pprint
import pandas as pd

############
# Utilities
############
import inspect
def print_location():
  """Prints the filename and line number of the caller."""
  frameinfo = inspect.getframeinfo(inspect.currentframe().f_back)
  print(f"File: {frameinfo.filename}, Line: {frameinfo.lineno}")

"""### Load DFL graphs (1000 Genomes)

"""

# from IPython.display import Image
# Image(url='https://github.com/pegasus-isi/1000genome-workflow/raw/master/docs/images/1000genome.png?raw=true', width=600)

# from google.colab import drive
# drive.mount('/content/drive')

#dfl_1kgenome = nx.read_graphml('1kgenome_1st_volume.graphml')
graphml1 = nx.read_graphml('data/1k_genome_example2.graphml')
idx = 0
dfl_1kgenome = []
dfl_1kgenome.append(graphml1)

# # test
# print(f"\ngraphml1:\n{graphml1}")
# # end test

# dfl_1kgenome.append(nx.read_graphml('/content/drive/MyDrive/oddite/1kgenome_2nd_volume.graphml'))
# dfl_1kgenome.append(nx.read_graphml('/content/drive/MyDrive/oddite/1kgenome_3rd_volume.graphml'))

#dfl_1kgenome_2nd = nx.read_graphml('1kgenome_2nd_volume.graphml')
#dfl_1kgenome_3rd = nx.read_graphml('1kgenome_3rd_volume.graphml')

"""### 1. Identify vertices/edges by Edge Types (fan-in, fan-out, sequential)"""

def find_edge_type(dfl):
  """returns vertex/edge per edge type from DFL

    Args:
        dfl (Graph): DataFlow Lifecycles.

    Returns:
        (fout [list], fin [list], seq [list]): vertices identified per edge type.
  """
  fout, fin, seq = [], [], []
  visited = []

  # # test
  # print(f"\ndfl.nodes\n{dfl.nodes}")
  # print(f"\ndfl.nodes.data()\n{dfl.nodes.data()}")
  # # end test

  for data_u, attr in dfl.nodes(data=True):
    task_v_list = []
    if attr['ntype'] != 'file':
      continue
    # # test
    # print()
    # print(f"data_u: {data_u} attr: {attr}")
    # # end test
    out_degree = dfl.out_degree(data_u)
    if out_degree > 1:
      # todos
      # 1. successors are not always in fan-out, e.g., file 1 - task 1 - file 2 (output) - task 2 (with reading 'file 1' again)
      # 2. mixed tasks should be grouped by e.g., file 1 - task group a, task group b (should be separated)
      task_v_list = [x for x in dfl.successors(data_u)]
      fout.append([data_u, task_v_list])
    elif out_degree == 1:
      _, task_v = list(dfl.edges(data_u))[0]
      in_degree = dfl.in_degree(task_v)
      if in_degree > 1 and task_v not in visited:
        data_u_list = [x for x in dfl.predecessors(task_v)]
        fin.append([data_u_list, task_v])
        #print(data_u_list, task_v)
        visited.append(task_v)
      elif in_degree == 1:
        seq.append([data_u, task_v])
      elif task_v in visited:
        continue
      else:
        print(data_u, task_v)
        continue
    else:
      # last data vertex, no outdegree
      seq.append([data_u, None])
  return fout, fin, seq

fout=[]
fin=[]
seq=[]
for id in range(len(dfl_1kgenome)):
  tmp = find_edge_type(dfl_1kgenome[id])
  fout.append(tmp[0])
  fin.append(tmp[1])
  seq.append(tmp[2])

# test
print("\nfout")
pprint(fout)
print("\nfin")
pprint(fin)
print("\nseq")
pprint(seq)
# end test

def vertex_groupby(node_list):
  res = {}
  for x in node_list:
    key = x.rsplit("_", 1)[0]
    if key not in res:
      res[key] = [x]
    else:
      res[key].append(x)
  return res.values()

"""### 2. Create Compound Graph per Edge Type"""

def create_compound_fout(dfl, attr):
  g = nx.DiGraph()
  d_u, t_v_lists = attr[0], attr[1]
  for t_v_list in vertex_groupby(t_v_lists):
    vols = []
    new_v_name = t_v_list
    v_org_name = ""
    for node in t_v_list:
      vols.append(dfl[d_u][node]['weight'])
    if len(t_v_list) > 1:
      new_v_name = "{} ({})".format(t_v_list[0].rsplit('_', 1)[0], len(vols))
      v_ntype = dfl.nodes[t_v_list[0]]['ntype']
      v_org_name = t_v_list[0]
    else:
      # skip for 1 instance of task
      continue
    if 'weight' in dfl.nodes[d_u]:
      data_size = dfl.nodes[d_u]['weight']
    else:
      data_size = 1024 # default byte size as a filler in case of missing
    avg_vol = sum(vols)/len(vols)
    g.add_node(d_u, weight=data_size, ntype=dfl.nodes[d_u]['ntype'])
    g.add_node(new_v_name, ntype=v_ntype, first_node_name=v_org_name)
    g.add_edge(d_u, new_v_name, weight=[avg_vol],
              volume=vols,
              etype='fout',
              ntasks=[len(vols)],
              data_size=data_size)
  return g

def create_compound_fin(dfl, attr):
  g = nx.DiGraph()
  d_u_list, t_v = attr[0], attr[1]

  # test
  print("\nd_u_list")
  pprint(d_u_list)
  print("\nt_v")
  pprint(t_v)
  # end test

  vols = []
  for node in d_u_list:

    # test
    print("\ndfl[node][t_v]")
    print(f"node: {node} t_v: {t_v}")
    pprint(dfl[node][t_v])
    # end test

    # New version
    # We only considered the edge that has a `weight`, what if not has?
    if 'weight' not in dfl[node][t_v]:
      vols.append(171717)
      continue
    # end New version

    vols.append(dfl[node][t_v]['weight'])
  if len(d_u_list) > 1:
    new_u_name = "{} ({})".format(d_u_list[0], len(d_u_list))
    u_ntype = dfl.nodes[d_u_list[0]]['ntype']
    u_org_name = d_u_list[0]
  else:
    # skip for 1 instance of task

    # test
    print("\ng empty")
    pprint(g.edges)
    # end test

    return g
    #new_u_name = d_u_list
    #u_ntype = 'file'
  if 'weight' in dfl.nodes[t_v]:
    data_size = dfl.nodes[t_v]['weight']
  else:
    data_size = 1024 # default byte size as a filler in case of missing
  g.add_node(new_u_name, ntype=u_ntype, first_node_name=u_org_name)
  g.add_node(t_v, weight=data_size, ntype=dfl.nodes[t_v]['ntype'])
  g.add_edge(new_u_name, t_v, weight=[sum(vols)/len(vols)], volume=vols, etype='fin', ntasks=[len(vols)])

  # test
  print("\ng normal")
  pprint(g.edges)
  print("\ng[new_u_name][t_v]")
  print(f"new_u_name: {new_u_name} t_v: {t_v}")
  pprint(g[new_u_name][t_v])
  # end test

  return g

"""#### Fan-out edge
One chromosome data vertex connects to Four 'individuals' task vertices
"""

# test
# print("\nfout[0][1]")
# pprint(fout[0][1])
# print("\nfout[0][3]")
# pprint(fout[0][3])
# end test

# compound_fout = create_compound_fout(dfl_1kgenome[0], fout[0][1])
fout_case = fout[0][3]
compound_fout = create_compound_fout(dfl_1kgenome[0], fout_case)

print("\ncompound_fout.nodes(data=True)")
pprint(compound_fout.nodes(data=True))

print("\nlist(compound_fout.edges(data=True))")
pprint(list(compound_fout.edges(data=True)))

"""#### Fan-in edge
Four output data vertices connect to One 'individuals_merge' task vertex
"""

# # test
# print("\nfin[0][0]")
# pprint(fin[0][0])
# print("\nfin[0][1]")
# pprint(fin[0][1])
# # end test

# compound_fin = create_compound_fin(dfl_1kgenome[0], fin[0][0])
fin_case = fin[0][1]
compound_fin = create_compound_fin(dfl_1kgenome[0], fin_case)
pprint(list(compound_fin.edges(data=True)))

# def plot_g(G, metric='weight'):
#   pos = nx.spring_layout(G)
#   pos = {'ALL.chr1.250000.vcf': (0, 0),
#          'individuals (4)': (1,0)}
#   nx.draw(G, pos, node_color=['blue', 'red'], with_labels=True)
#   edge_labels = nx.get_edge_attributes(G,metric)
#   nx.draw_networkx_edge_labels(G, pos, edge_labels =  edge_labels)
#   plt.show()

# def plot_g_fin(G, metric='weight'):
#   pos = nx.spring_layout(G)
#   pos = {'chr1n-1-2.tar.gz (4)': (0, 0),
#          'individuals_merge_ID0000005': (1,0)}
#   nx.draw(G, pos, node_color=['blue', 'red'], with_labels=True)
#   edge_labels = nx.get_edge_attributes(G,metric)
#   nx.draw_networkx_edge_labels(G, pos, edge_labels =  edge_labels)
#   plt.show()

# def plot_1k_sub(g, fout):
#   g_new = nx.DiGraph()
#   pos = {'ALL.chr1.250000.vcf': (0, 0)}
#   for idx, node in enumerate(fout[1]):
#     w = g[fout[0]][fout[1][idx]]['weight']
#     g_new.add_edge(fout[0], fout[1][idx], weight=w)
#     pos[node] = (1, idx)
#   nx.draw(g_new, pos, node_color=['blue'] + ['red'] * 4, with_labels=True)
#   edge_labels = nx.get_edge_attributes(g_new,'weight')
#   nx.draw_networkx_edge_labels(g_new, pos, edge_labels = edge_labels)
#   plt.show()
#   return g_new
# # g_1k_fout = plot_1k_sub(dfl_1kgenome[0], fout[0][1])
# g_1k_fout = plot_1k_sub(dfl_1kgenome[0], fout_case)

# plot_g(compound_fout, 'weight')

# plot_g(compound_fout, 'ntasks')

# def plot_1k_sub_fin(g, fin):
#   g_new = nx.DiGraph()
#   pos = {'individuals_merge_ID0000005': (1, 0)}
#   for idx, node in enumerate(fin[0]):
#     w = g[fin[0][idx]][fin[1]]['weight']
#     g_new.add_edge(fin[0][idx], fin[1], weight=w)
#     pos[node] = (0, idx)
#   nx.draw(g_new, pos=pos, node_color=['blue', 'red'] + ['blue']* 3, with_labels=True)
#   edge_labels = nx.get_edge_attributes(g_new,'weight')
#   nx.draw_networkx_edge_labels(g_new, pos, edge_labels = edge_labels)
#   plt.show()
#   return g_new
# # g_1k_fin = plot_1k_sub_fin(dfl_1kgenome[0], fin[0][0])
# g_1k_fin = plot_1k_sub_fin(dfl_1kgenome[0], fin_case)

# plot_g_fin(compound_fin)

"""### 3. Detect the Rules"""

def get_source_node(compound):
  if len(list(compound.nodes)) > 0:
    return list(compound.nodes)[0]
  else:
    return []

def get_target_node(compound):
  if len(list(compound.nodes)) > 1:
    return list(compound.nodes)[1:]
  else:
    return []

def get_first_node_name(g, name):
  try:
    return name.rsplit(' ', 1)[0]
  except:
    return name

def fanout_normal_scaling(dfl, u):
  outdegree_u = dfl.out_degree(u)
  if 'weight' in dfl.nodes[u]:
    n_u = dfl.nodes[u]['weight']
  else:
    n_u = dfl.out_degree(u, weight='weight') # sum of 'volume' from weight edge attributes
  return n_u / outdegree_u

def fanout_fixed_vol_xfer(dfl, u):
  if 'weight' in dfl.nodes[u]:
    n_u = dfl.nodes[u]['weight']
  else:
    n_u = dfl.out_degree(u, weight='weight') # sum of 'volume' from weight edge attributes
  return n_u

def fanout_fixed_rule_check(dfl, compound, fout, summary=True):
  u = get_source_node(compound)#fout[0]
  v_s = get_target_node(compound)#fout[1]
  res = []
  if len(u) == 0:
    return res
  for u, v in compound.edges():
    predicted_val = fanout_fixed_vol_xfer(dfl, u)
    #for v in v_s:
    if v not in dfl.nodes:
      v_first = compound.nodes[v]['first_node_name']
    actual_val = dfl.get_edge_data(u, v_first, 0)['weight']
    diff_val = predicted_val / actual_val
    res.append([u, v, predicted_val, actual_val, diff_val])
  #if summary:
  #  diff_list = [x[4] for x in res]
  #  return [res[0][0], get_target_node(compound), res[0][2], res[0][3], sum(diff_list)/len(diff_list)]
  #else:
  return res

def fanout_normal_rule_check(dfl, compound, fout, summary=True):
  u = get_source_node(compound)
  #v = get_target_node(compound)
  v_s = fout[1]
  res = []
  if len(u) == 0:
    return res
  #for v in v_s:
  for u, v in compound.edges():
    if v not in dfl.nodes:
      v_first = compound.nodes[v]['first_node_name']
    predicted_val = fanout_normal_scaling(dfl, u)
    actual_val = dfl.get_edge_data(u, v_first, 0)['weight']
    diff_val = predicted_val / actual_val
    res.append([u, v, predicted_val, actual_val, diff_val])
    #print(res)
  #if summary:
  # diff_list = [x[4] for x in res]
  #  return [res[0][0], get_target_node(compound), res[0][2], res[0][3], sum(diff_list)/len(diff_list)]
  #else:
  return res

def fanin_scaling(dfl, u, v):
  indegree_v = dfl.in_degree(v)
  '''
  if 'weight' in dfl.nodes[u]:
    n_v = dfl.nodes[u]['weight']
  else:
  '''
  n_v = dfl.in_degree(v, weight='weight')
  return n_v / indegree_v

def fanin_normal_rule_check(dfl, compound):
  #u = get_source_node(compound)
  #v = get_target_node(compound)
  #print(u,v)

  # # test
  # print("\ncompound")
  # pprint(compound)
  # # end test

  res = []
  for u, v in compound.edges():
    u_first = get_first_node_name(dfl, u)
    if len(u) > 0 and len(v) > 0:
      predicted_val = fanin_scaling(dfl, u, v)

      # test
      print("\ndfl[u_first][v]")
      pprint(dfl[u_first][v])
      # end test

      # Old version
      # actual_val = dfl.get_edge_data(u_first, v, 0)['weight']
      # New version
      if 'weight' in dfl[u_first][v]:
        actual_val = dfl[u_first][v]['weight']
      else:
        actual_val = compound[u][v]['weight'][0]
      # end New version

      diff_val = predicted_val / actual_val
      res.append([u, v, predicted_val, actual_val, diff_val])
  return res

print("\ncompound_fin.nodes(data=True)")
pprint(compound_fin.nodes(data=True))

fanin_rule_checked = fanin_normal_rule_check(dfl_1kgenome[0], compound_fin)

fanin_df = pd.DataFrame(fanin_rule_checked, columns=['source vertex (u, producer)','target vertex (v, consumer)','predicted volume (byte)','actual volume (byte)','ratio (%)'])
fanin_df.style.format({
    'predicted volume (byte)': '{0:,.2f}'.format,
    'actual volume (byte)': '{0:,.2f}'.format,
  'ratio (%)': '{:,.2%}'.format,
})
print("\nfanin_df")
print(fanin_df)

def get_output_fanout(dfl, fout, DEBUG=False):
  dfl_output = []
  for f in fout:
    comp = create_compound_fout(dfl, f)
    fns = fanout_normal_rule_check(dfl, comp, f)
    ffs = fanout_fixed_rule_check(dfl, comp, f)
    for idx in range(len(fns)):
      fn = fns[idx]
      ff = ffs[idx]
      #print(len(fn), len(ff), fn, ff)
      if len(fn) > 4:
        eq1_dist = abs(fn[4] - 1)
      else:
        continue
      if len(ff) > 4:
        eq2_dist = abs(ff[4] - 1)
      else:
        continue
      if eq1_dist > eq2_dist:
        print ("Rule 2 applies to {}".format(ff[:2])) if DEBUG is True else ''
        tmp = ff + ['Rule 2']
      else:
        print ("Rule 1 applies to {}".format(fn[:2])) if DEBUG is True else ''
        tmp = fn + ['Rule 1']
      dfl_output.append(tmp)
  return dfl_output

dfl_output_1kgenome_fout_1st = get_output_fanout(dfl_1kgenome[0], fout[0], DEBUG=True)
dfl_1kgenome[0].edges(data=True)

print("\ndfl_1kgenome[0].edges(data=True)")
pprint(dfl_1kgenome[0].edges(data=True))


class correctionFactor():
  data_ref = {}
  data = []
  def __init__(self, data):
    self._fit(data)
  def _fit(self, data):
    for d in data:
      print(d)
      u = d[0].rsplit(" ", 1)[0]
      v = d[1].rsplit(" ", 1)[0]
      p = d[2] # predicted
      a = d[3] # actual
      r = d[4] # ratio
      n = d[5] # rule name
      tmp = {'predicted': p,
                          'actual': a,
                          'repeated': round(1/r, 2),
                          'rule': n}
      if u in self.data_ref:
        self.data_ref[u][v] = tmp
      else:
        self.data_ref[u] = {v:tmp}

  def fit(self, data):
    self.data.append(data)
  def transform(self, data):
    for idx, d in enumerate(data):
      u = d[0].rsplit(" ", 1)[0]
      v = d[1].rsplit(" ", 1)[0]
      p = d[2] # predicted
      a = d[3] # actual
      r = d[4] # r
      n = d[5] # rule name
      try:
        r = self.data_ref[u][v]['repeated']
        prev_n = self.data_ref[u][v]['rule']
        if prev_n != n:
          print ("rule donot match", prev_n, n, u, v)
      except:
        r = 1/r
        print(f'err in repeated, {r}')

      n = (p * r) # new predicted
      u = n / a # updated ratio
      data[idx] = d[:6] + [n, u]
    return data
  def print(self):
    return self.data_ref

def get_output_fanin(dfl, fin):
  print_location()
  dfl_output = []
  for f in fin:
    # test
    print("\nf")
    pprint(f)
    # end test
    comp = create_compound_fin(dfl, f)
    fns = fanin_normal_rule_check(dfl, comp)
    for fn in fns:
      tmp = fn + ['Rule 3']
      dfl_output.append(tmp)
  return dfl_output

dfl_output_1kgenome_fin_1st = get_output_fanin(dfl_1kgenome[0], fin[0])

print_location()

print("\ndfl_output_1kgenome_fin_1st")
pprint(dfl_output_1kgenome_fin_1st)

print("\ndfl_output_1kgenome_fout_1st")
pprint(dfl_output_1kgenome_fout_1st)

dfl_output_1kgenome_1st = dfl_output_1kgenome_fout_1st + dfl_output_1kgenome_fin_1st
cfactor = correctionFactor(dfl_output_1kgenome_1st)
out_list = cfactor.transform(dfl_output_1kgenome_1st)

print("\ncfactor.data_ref")
pprint(cfactor.data_ref)

print_location()

dfl_output_1kgenome_fout = []
dfl_output_1kgenome_fin = []
for id in range(len(dfl_1kgenome)):
  dfl_output_1kgenome_fout.append(get_output_fanout(dfl_1kgenome[id], fout[id]))
  dfl_output_1kgenome_fin.append(get_output_fanin(dfl_1kgenome[id], fin[id]))

cfactor.transform(dfl_output_1kgenome_fin[1])

cfactor.transform(dfl_output_1kgenome_fout[1])

dfl_output_1kgenome_fout[0][3],dfl_output_1kgenome_fout[1][3]

for idx in range(len(dfl_output_1kgenome_fout)):
  tmp = sum([x[2]['weight'] for x in dfl_1kgenome[idx].edges('ALL.chr1.250000.vcf', data=True) if x[1][:len('individuals')] == 'individuals'])
  print(tmp)

tmp_fout = {}
tmp_fin = {}
for id in range(len(dfl_output_1kgenome_fout)):
  instance = dfl_output_1kgenome_fout[id]
  tmp_fout[id] = {'Rule 1':{'edge_cnt':[], 'tname':[], 'dname':[], 'producer-consumer':[]},
             'Rule 2': {'edge_cnt':[], 'tname':[], 'dname':[], 'producer-consumer':[]},
         #    'Rule 3': {'edge_cnt':[], 'tname':[], 'dname':[], 'producer-consumer':[]}
             }
  for fout in instance:
    tname, t = fout[1].rsplit('(', 1)
    e_cnt = int(t.rsplit(')', 1)[0])
    #print(id, fout[5],tmp, e_cnt, t, fout[1])
    tmp_fout[id][fout[5]]['edge_cnt'].append(e_cnt)
    tmp_fout[id][fout[5]]['tname'] = list(set(tmp_fout[id][fout[5]]['tname'] + [tname.rstrip()]))
    tmp_fout[id][fout[5]]['dname'] = list(set(tmp_fout[id][fout[5]]['dname'] + ['*.' + fout[0].rsplit('.',1)[1]]))
    #print(tmp_fout[id][fout[5]]['producer-consumer'], [tname.rstrip(), '*.' + fout[0].rsplit('.',1)[1]])
    tmp_fout[id][fout[5]]['producer-consumer'] = list(set(['*.' + fout[0].rsplit('.',1)[1] + ' - ' + tname.rstrip()] + tmp_fout[id][fout[5]]['producer-consumer']))
for id in range(len(dfl_output_1kgenome_fin)):
  instance = dfl_output_1kgenome_fin[id]
  tmp_fin[id] = {#'Rule 1':{'edge_cnt':0, 'tname':[], 'dname':[], 'producer-consumer':[]},
             #'Rule 2': {'edge_cnt':0, 'tname':[], 'dname':[], 'producer-consumer':[]},
             'Rule 3': {'edge_cnt':[], 'tname':[], 'dname':[], 'producer-consumer':[]}
             }
  for fin in instance:
    dname, t = fin[0].rsplit('(', 1)
    e_cnt = int(t.rsplit(')', 1)[0])
    #print(id, fout[5],tmp, e_cnt, t, fout[1])
    tmp_fin[id][fin[5]]['edge_cnt'].append(e_cnt)
    tmp_fin[id][fin[5]]['tname'] = list(set(tmp_fin[id][fin[5]]['tname'] + [fin[1].rsplit('_',1)[0]]))
    tmp_fin[id][fin[5]]['dname'] = list(set(tmp_fin[id][fin[5]]['dname'] + [dname.rstrip()]))
    #print(tmp_fout[id][fout[5]]['producer-consumer'], [tname.rstrip(), '*.' + fout[0].rsplit('.',1)[1]])
    tmp_fin[id][fin[5]]['producer-consumer'] = list(set(tmp_fin[id][fin[5]]['producer-consumer'] + ['*.' + dname.rsplit('.',1)[1] + ' - ' + fin[1].rsplit('_',1)[0]]))

def summary_per_task(dfl_output, output, etype, groupby='consumer'):
  tmp = []
  res = []
  degree = {}
  for id in range(len(dfl_output)):
    for k,v in output[id].items():
      #print(k,v)
      if groupby == "consumer":
        for i, tname in enumerate(v['tname']):
          x = f'* -> {tname}'
          tmp.append(x)
          if x not in degree:
            degree[(id + 1, x)] = v['edge_cnt'][i]
          else:
            degree[(id + 1, x)] += v['edge_cnt'][i]
      else:
        tmp += v['producer-consumer']
        for i, x in enumerate(v['producer-consumer']):
          if x not in degree:
            degree[(id + 1, x)] = v['edge_cnt'][i]
          else:
            degree[(id + 1, x)] += v['edge_cnt'][i]
          #print (id + 1, x)
    tmp = list(set(tmp))
    #print (degree)
    for i in tmp:
      if (id + 1, i) in degree:
        res.append([f'instance {id+1}', i, degree[(id+1, i)], etype])
  return res

summary_per_task(dfl_output_1kgenome_fout, tmp_fout, 'fan-out', groupby='consumer')

df_fout_producer_focused = pd.DataFrame(summary_per_task(dfl_output_1kgenome_fout, tmp_fout, 'fan-out', groupby='producer'),
                                        columns=['Instance ID', 'Producer-Consumer', 'Degree', 'Pattern']).sort_values(['Producer-Consumer', 'Instance ID'])
df_fout_consumer_focused = pd.DataFrame(summary_per_task(dfl_output_1kgenome_fout, tmp_fout, 'fan-out', groupby='consumer'),
                                        columns=['Instance ID', 'Producer-Consumer', 'Degree', 'Pattern']).sort_values(['Producer-Consumer', 'Instance ID'])
df_fout_producer_focused.reset_index(inplace=True, drop=True)
df_fout_consumer_focused.reset_index(inplace=True, drop=True)

df_fin_producer_focused = pd.DataFrame(summary_per_task(dfl_output_1kgenome_fin, tmp_fin, 'fan-in', groupby='producer'),
                                       columns=['Instance ID', 'Producer-Consumer', 'Degree',  'Pattern']).sort_values(['Producer-Consumer', 'Instance ID'])
df_fin_consumer_focused = pd.DataFrame(summary_per_task(dfl_output_1kgenome_fin, tmp_fin, 'fan-in', groupby='consumer'),
                                       columns=['Instance ID', 'Producer-Consumer', 'Degree', 'Pattern']).sort_values(['Producer-Consumer', 'Instance ID'])
df_fin_producer_focused.reset_index(inplace=True, drop=True)
df_fin_consumer_focused.reset_index(inplace=True, drop=True)

summary_per_task(dfl_output_1kgenome_fout, tmp_fout, 'fan-out', groupby='consumer')

def dfl_summary(dfls):
  res = []
  for idx, dfl in enumerate(dfls):
    edge_cnt = len(list(dfl.edges()))
    node_cnt = len(list(dfl.nodes()))
    tnode_cnt = sum([1 for n, attr in dfl.nodes(data=True) if attr['ntype'] == 'task'])
    dnode_cnt = node_cnt - tnode_cnt
    all_filesizes = sum([attr['weight'] for n, attr in dfl.nodes(data=True) if ('weight' in attr)])
    input_filesizes = sum([attr['weight'] for n, attr in dfl.nodes(data=True) if ('weight' in attr) and (dfl.in_degree(n) == 0)])
    output_filesizes = sum([attr['weight'] for n, attr in dfl.nodes(data=True) if ('weight' in attr) and (dfl.out_degree(n) == 0)])
    volume_total = sum([attr['weight'] for u, v, attr in dfl.edges(data=True)])
    res.append([idx + 1, edge_cnt, node_cnt, all_filesizes, input_filesizes, output_filesizes, dnode_cnt, tnode_cnt, volume_total])
  return res

dfls_summary_list = dfl_summary(dfl_1kgenome)
df_dfls_summary = pd.DataFrame(dfls_summary_list, columns=['Instance ID', '# Edges', '# Nodes', 'Data Size (byte)', 'Input Data (byte)', 'Output Data (byte)', '# Data', '# Tasks', 'Volume (byte)'])
df_dfls_summary.style.format({
    'Volume (byte)': '{0:,.2f}'.format,
    'Input Data (byte)': '{0:,.2f}'.format,
    'Output Size (byte)': '{0:,.2f}'.format,
})

df_dfls_summary[['Instance ID', '# Edges', '# Nodes', 'Data Size (byte)']].style.format({
    'Volume (byte)': '{0:,.0f}'.format,
    'Data Size (byte)': '{0:,.0f}'.format,
    'Input Data (byte)': '{0:,.0f}'.format,
    'Output Size (byte)': '{0:,.0f}'.format,
})

df_dfls_summary.style.format({
    'Volume (byte)': '{0:,.0f}'.format,
    'Data Size (byte)': '{0:,.0f}'.format,
    'Input Data (byte)': '{0:,.0f}'.format,
    'Output Size (byte)': '{0:,.0f}'.format,
})

# output file sizes
#for node in dfl_1kgenome[0].nodes:
#  print(dfl_1kgenome[0].out_degree(node), node)

#pd.concat([df_fout_producer_focused, df_fin_producer_focused])

df_tmp = pd.concat([df_fout_consumer_focused, df_fin_consumer_focused])
df_tmp[df_tmp['Instance ID'] != 'instance 3'].reset_index(drop=True)

df_fout_consumer_focused

df_summary = pd.concat([df_fout_consumer_focused, df_fin_consumer_focused], ignore_index=True)
df_summary_1 = df_summary[df_summary['Instance ID'] == 'instance 1']
df_summary_1.reset_index(inplace=True,drop=True)
df_summary_1

df_summary_producer = pd.concat([df_fout_producer_focused, df_fin_producer_focused], ignore_index=True)
df_summary_p1 = df_summary_producer[df_summary_producer['Instance ID'] == 'instance 1']
df_summary_p1.reset_index(inplace=True,drop=True)
#df_summary_p1.sort_values('Producer-Consumer', ascending=False)
df_summary_p1

def between_compound(dfl_outputs, pattern='fout'):
  res = {}
  for idx, dfl_output in enumerate(dfl_outputs[:-1]):
    res_tmp = []
    for entry in dfl_output:
      if len(entry) == 6:
        u, v, pred_v, act_v, ratio, rule = entry
      else:
        u, v, pred_v, act_v, ratio, rule, updated_pred_v, updated_ratio = entry
      if pattern == 'fin':
        name_n_cnt = u
      else:
        name_n_cnt = v
      _name, _cnt = name_n_cnt.rsplit(' ', 1)
      _cnt = _cnt.split('(')[1]
      _cnt = _cnt.split(')')[0]
      if pattern == 'fin':
        v_name = v.rsplit("_", 1)[0]
        pc = f"* -> {v_name}"
      else:
        pc = f"* -> {_name}"
      if pc not in res:
        res[pc] = [pc] + [0 for x in range(2 * (len(dfl_outputs) -1))] + [[]]
      res[pc][idx + 1] += act_v
      #print(res[pc][idx + 3], idx)
      res[pc][idx + 3] += int(_cnt)
      res[pc][-1] = (list(set(res[pc][-1] + [rule])))
      #print(res[pc])
  return res

between_compound(dfl_output_1kgenome_fout, 'fout')

fin_tmp = list(between_compound(dfl_output_1kgenome_fin, 'fin').values())
fout_tmp = list(between_compound(dfl_output_1kgenome_fout, 'fout').values())
fall_tmp = fin_tmp + fout_tmp
for f in fall_tmp:
  f[5] = ' '.join(f[5]) if len(f[5]) == 1 else ', '.join(f[5])
df_template = pd.DataFrame(fall_tmp,
                           columns=['Producer-Consumer'] + [f'Instance {x+1}\'s Volume' for x in range(2)] +
                           [f'Instance {x+1}\'s Degree' for x in range(2)] + ['Rule applied'])
df_template.head(2).style.format({
    'Instance 1\'s Volume': '{0:,.0f}'.format,
    'Instance 2\'s Volume': '{0:,.0f}'.format,

})



2852238*4,5705025*2

tmp_fout[1]

res = [] # fanout - rule 1, rule 2, fan in - rule 3
for k1, v1 in tmp_fout.items():
  r = {'Rule 1': [],
       'Rule 2': [],
       'Rule 3': []}
  for rule, v2 in v1.items():
    for item in v2['producer-consumer']:
      print(item, rule, k1)
      r[rule].append(['fan-out', item, rule])
print(r)

dfl_output_1kgenome_fout

dfl_1kgenome[0].edges(data=True)

tmp_fout[0]['Rule 2']

#pd.DataFrame([tmp_fout[0]['Rule 1']['producer-consumer']] + [tmp_fout[1]['Rule 1']['producer-consumer']] +
#             [tmp_fout[2]['Rule 1']['producer-consumer']],
#             columns=['fanout (rule 1)', 'fanout (rule 1)'],
#             index=['1k Genomes (DFL Instance 1)', '1k Genomes (DFL Instance 2)', '1k Genomes (DFL Instance 3)'])

[tmp_fout[0]['Rule 1']['producer-consumer']] + [tmp_fout[1]['Rule 1']['producer-consumer']]

#updated_dfl_output_1kgenome = []
#for d in dfl_output_1kgenome:
#  updated_dfl_output_1kgenome.append([d[0], d[1], d[6], d[3], d[7], d[5]])

dfl_output_1kgenome_org = []
for r in dfl_output_1kgenome_1st:
  dfl_output_1kgenome_org.append(r[:6])

dfl_df = pd.DataFrame(dfl_output_1kgenome_org, columns=['source vertex (u, producer)','target vertex (v, consumer)',
                                           'predicted volume (byte)','actual volume (byte)',
                                           'ratio (%)', 'Rule applied'])
dfl_df.style.format({
    'predicted volume (byte)': '{0:,.2f}'.format,
    'actual volume (byte)': '{0:,.2f}'.format,
    'ratio (%)': '{:,.2%}'.format,
})

Image('/content/drive/MyDrive/oddite/1kgenome_dfl.png')

#pd.DataFrame(fanout_fixed_rule_check(g_1kgenome, compound_fout, fout[1]), columns=['source vertex','target vertex','predicted value','actual value','difference in ratio'])

def find_leftover_nodes(dfl, nlist):
  full_nodes = [x for x in dfl.nodes]
  for node in nlist:
    if node in full_nodes:
      full_nodes.remove(node)
  return full_nodes

def flatten(nlist):
  res = []
  for u, v in nlist:
    if isinstance(v, list):
      res.append(u)
      res += v
    elif isinstance(u,list):
      res += u
      res.append(v)
    else:
      res.append(u)
      if v is not None:
        res.append(v)
  return list(set(res))

flattened_nodes = flatten(fout[0]) + flatten(fin[0]) + flatten(seq[0])
leftover_nodes = find_leftover_nodes(dfl_1kgenome[0], flattened_nodes)

ncnt = len(list(dfl_1kgenome[0].nodes))
ncnt, len(flattened_nodes), len(leftover_nodes)

len(flatten(fout[0])), len(flatten(fin[0])), len(flatten(seq[0]))

#fout, fin, seq = find_edge_type(dfl_montage)
 #len(flatten(fout)), len(flatten(fin)), len(flatten(seq))

# import networkx as nx
# import pandas as pd

def get_node_count(g):
  nodes = {}
  for node, val in g.nodes(data=True):
      if val['ntype'] != 'task':
          continue
      node_name = node.split("_")[0]
      if node_name in nodes:
          nodes[node_name] += 1
      else:
          nodes[node_name] = 1
  return nodes

def get_edge_count(g):
  edges = {}
  for u, v, val in g.edges(data=True):
  #    if u[:8] == 'mProject':
  #        print(u,v,val)
      u_name = u.split("_")[0]
      if u_name in nodes:
          if u_name in edges:
              edges[u_name] += 1
          else:
              edges[u_name] = 1
      v_name = v.split("_")[0]
      if v_name in nodes:
          if v_name in edges:
              edges[v_name] += 1
          else:
              edges[v_name] = 1

  return edges

def get_nodes(g):
    nodes = {}
    for node, val in g.nodes(data=True):
        if val['ntype'] != 'task':
            continue
        node_name = node.split("_")[0]
        if node_name in nodes:
            nodes[node_name] += 1
        else:
            nodes[node_name] = 1
    return nodes

def get_edges(g):
    edges = {}
    nodes = get_nodes(g)
    for u, v, val in g.edges(data=True):
        u_name = u.split("_")[0]
        if u_name in nodes:
            if u_name in edges:
                edges[u_name] += 1
            else:
                edges[u_name] = 1
        v_name = v.split("_")[0]
        if v_name in nodes:
            if v_name in edges:
                edges[v_name] += 1
            else:
                edges[v_name] = 1

    return edges

def edge_count(edges):
    cnt = 0
    for i, j in edges.items():
        cnt += j
    return cnt

#g_deepdrivemd = nx.read_graphml('deepdrivemd_1st_volume.graphml')

def ratio_print(total, elist):
    return "{:.0f} %".format((sum(elist)/total)*100)
def count_print(total, elist):
    return "{}/{}".format(sum(elist), total)
def mixed_print(total, applied, rule):
  return "{}/{} edges".format(total, applied, rule)
  #return "{} edges ({:.0f}% by {})".format(total, (total/applied)*100, rule)
def percent_print(total, applied):
    return "{:.0f} %".format((applied/total)*100)

import pandas as pd

df_v1 = pd.DataFrame({'Total edges': [273, 89, 398, 38],
                   'Rule 1-3': [ratio_print(273, [72, 108, 36]), ratio_print(89, [17]), '',ratio_print(38, [12,13])],
                   'Rule 4': ['', '', ratio_print(398,[192,192]), ''],
                   'Rule 5-6': [ratio_print(273, [6, 15, 33, 3]),
                              ratio_print(89, [35, 35, 2]),
                              ratio_print(398, [2]),
                               ratio_print(38, [11,2])]},
                  index=['Montage', '1000 Genomes', 'SRA Search', 'DeepDriveMD'])

df = pd.DataFrame({#85, 30, 63
                   # 29, 5, 16
                   # 96, 96, 96
                   # (3+12, 16, 10)
                   'Fan-out': [mixed_print(85, 85, 'eq. 1'), mixed_print(29, 29, 'eq. 2'), mixed_print(96, 96, 'eq. 5 *'), mixed_print(15, 15, 'eq. 2')],
                   'Fan-in': [mixed_print(30, 30, 'eq. 3'), mixed_print(5, 5, 'eq. 3'), mixed_print(96, 96, 'eq. 3'), mixed_print(16,16,'eq. 3')],
                   'Series': [mixed_print(63, 63, 'eq. 4'),
                              mixed_print(16, 16, 'eq. 4'),
                              mixed_print(206, 206, 'eq. 4'),
                              mixed_print(10, 10, 'eq. 4')],
                   'Remainder': ['-','-','x/x edges', '-'],
                   'Coverage': [percent_print(169,163), percent_print(50, 50), percent_print(398, 398), percent_print(38, 38)]},
                  index=['Montage', '1000 Genomes', 'SRA Search *', 'DeepDriveMD'])

"""# Coverage in Table (Volumes)"""

df

"""* SRA Search applies a dynamic information (by eq. 5)"""