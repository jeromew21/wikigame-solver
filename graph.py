import networkx as nx
import pylab as plt
from networkx.drawing.nx_agraph import graphviz_layout, to_agraph
import pygraphviz as pgv
import random

from populate import DB, DELIMITER, sqlite3

LIMIT = 10000


class WikiNode:
    def __init__(self, url, c):
        self.url = url
        c.execute(f"SELECT name, children FROM pages WHERE url = ?", (url,))
        fetch = c.fetchall()
        self.name = "invalid"
        self.valid = True
        if not fetch:
            self.valid = False
        else:
            self.name = fetch[0][0]
            self.neighbor_urls = fetch[0][1].split(DELIMITER)[:LIMIT]
    
    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.url)

def expand(g, node, c, depth=1):
    g.add_node(node)
    print("expanding", node)
    for url in node.neighbor_urls:
        n_node = WikiNode(url, c)
        if not n_node.valid:
            print("bad node:", n_node)
            continue
        print("Adding edge {}->{}".format(node.name, n_node.name))

        g.add_node(n_node)
        g.add_edge(node, n_node)
        if depth > 0:
            expand(g, n_node, c, depth-1)

conn = sqlite3.connect(DB)
c = conn.cursor()
root = WikiNode("https://en.wikipedia.org/wiki/Adolf_Hitler", c)
G = nx.DiGraph()

expand(G, root, c, 0)

conn.commit()
conn.close()

G.graph['graph']={'rankdir':'TD'}
G.graph['node']={'shape':'circle'}
G.graph['edges']={'arrowsize':'4.0'}

A = to_agraph(G)
print(A)
A.layout('dot')
fileout = ''.join(random.choice(list("abcderdfs")) for i in range(4)) + ".png"
A.draw(fileout)
print(fileout)

