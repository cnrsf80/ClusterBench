import base64
import os
from math import *
import clusterBench.tools as tools
from clusterBench import draw
import networkx as nx
import pandas as pd
from clusterBench.cluster import cluster
from clusterBench.algo import model
import numpy as np

#Representation d'un graphe
class network(model):
    graph:nx.Graph=None
    positions=None

    # def __init__(self,nodes,edges):
    #     self.graph=nx.Graph()
    #     self.graph.add_node(nodes)
    #     self.graph.add_edge(edges)

    def __init__(self,data=None,url:str="",remote_addr:str="",algo_loc:str=""):
        self.clusters.clear()
        if draw.colors is None or len(draw.colors) < 2: draw.colors = draw.init_colors(200)

        if len(url)>0:
            tools.progress(0,100,"Chargement du graphe")
            url=tools.getUrlForFile(url,remote_addr)
            if not self.load(url,algo_loc):
                if not self.graph is None:
                    self.graph = nx.convert_node_labels_to_integers(self.graph, label_attribute="name")

            if not self.graph is None:
                tools.progress(90,100,"Préparation")
                self.data: pd.DataFrame = pd.DataFrame(index=list(range(0,len(self.graph.nodes))))
                self.data["name"] = nx.get_node_attributes(self.graph,"name")

                self.dimensions = 3
                self.name_col = "name"

        if not data is None:
            super().__init__(data=data)
            self.graph=nx.Graph()



    def sphere_layout(self,r=1):
        alpha=0
        beta=0
        interval=4*pi/len(self.graph.nodes)
        positions=dict()
        for n in self.graph.nodes:
            alpha=alpha+pi/interval
            beta=beta+pi/interval
            positions[n]=[r*sin(alpha)*cos(beta),r*sin(alpha)*sin(beta),r*cos(alpha)]

        return positions
        #nx.set_node_attributes(self.graph, positions, "pos")



    # Positionnement des noeuds du graphe suivant l'algorithme gn,modularity,circular
    def relocate(self,dim=3,scale=3,method="spectral"):
        if "circular" in method: d = self.sphere_layout(r=1)
        if "spectral" in method:d=nx.spectral_layout(self.graph,dim=dim,scale=scale)
        if "fr" in method:d=nx.fruchterman_reingold_layout(self.graph,iterations=50,dim=3)
        if "random" in method:d=nx.random_layout(self.graph,dim=3)

        i=1
        pos=[]
        for n in self.graph.nodes:
            pos.append(str(list(d.get(i-1))))
            i = i + 1

        nx.set_node_attributes(self.graph, pos, "location")

        self.position=list(d.values())
        return d


    def save(self,path=""):
        if len(path)==0:path="./clustering/"+self.url+".gpickle"
        if not path.endswith(".gpickle"):path=path+".gpickle"
        nx.write_gpickle(self.graph,path)

    def savegml(self,name):
        url=tools.getPath(name,"public")
        if not url.endswith(".gml"):url=url+".gml"
        nx.write_graphml(self.graph,url)
        return url

    def create_graph_from_dataframe(self):
        df=self.data.apply(lambda x:(0,1)[x>self.seuil])
        self.graph=nx.from_numpy_matrix(df.as_matrix())


    def load(self,url,algo_loc=""):
        self.url=bytes(base64.encodebytes(bytes(url+algo_loc,encoding="utf-8"))).hex()
        if os.path.exists("./clustering/"+self.url+".gpickle"):
            tools.progress(50,100,"Chargement depuis le cache")
            self.graph = nx.read_gpickle("./clustering/"+self.url+".gpickle")
            return True
        else:

            url=tools.dezip(url)

            if ".gml" in url or ".graphml" in url :
                tools.progress(50, 100, "Chargement du fichier au format GML")
                try:
                    self.graph =nx.read_gml(url)
                except:
                    try:
                        self.graph=nx.read_graphml(url)
                    except:
                        return False


            if ".gexf" in url or ".gephi" in url:
                try:
                    self.graph = nx.read_gexf(url)
                except:
                    print("Impossible de lire "+url)


            if self.graph is None:
                tools.progress(50, 100, "Chargement depuis la matrice de distance")
                try:
                    self.data: pd.DataFrame = tools.get_data_from_url(url,"")
                except:
                    pass
                if not self.data is None:
                    self.create_graph_from_dataframe()
                    return True

            return False


    def node_treatments(self):
        G=self.graph
        tools.progress(0,100,"Degree de centralité")
        if len(nx.get_node_attributes(G,"centrality"))==0:
            nx.set_node_attributes(G,nx.degree_centrality(G),"centrality")

        tools.progress(20, 100, "Degree de betweeness")
        if len(nx.get_node_attributes(G, "betweenness")) == 0:
            nx.set_node_attributes(G, nx.betweenness_centrality(G), "betweenness")

        tools.progress(40, 100, "Degree de closeness")
        if len(nx.get_node_attributes(G, "closeness")) == 0:
            nx.set_node_attributes(G, nx.closeness_centrality(G), "closeness")

        tools.progress(60, 100, "Page rank")
        try:
            if len(nx.get_node_attributes(G, "pagerank")) == 0:
                nx.set_node_attributes(G, nx.pagerank(G), "pagerank")
        except:
            pass

        tools.progress(80, 100, "Hub and autorities")
        try:
            if len(nx.get_node_attributes(G, "hub")) == 0:
                hub, aut = nx.hits(G)
                nx.set_node_attributes(G, hub, "hub")
                nx.set_node_attributes(G, aut, "autority")
        except:
            pass

        #tools.progress(90, 100, "Excentricity")
        #nx.set_node_attributes(G, nx.eccentricity(G), "eccentricity")

        self.node_treatment=True
        tools.progress(100, 100, "Fin des traitements")


    def findClusters(self,prefixe="cl_",method="gn",k=5,iter=15):
        if not self.load_cluster(self.url+"_"+method+str(k)+str(iter)):
            tools.progress(0, 100, "Recherche des communautés avec "+method)

            #Initialisation a un cluster unique
            comm=[set(range(0,len(self.graph.nodes)))]

            if method.startswith("gn"):
                tmp=nx.algorithms.community.girvan_newman(self.graph)
                comm=tuple(sorted(c) for c in next(tmp))

            if method.startswith("lab"):
                comm=nx.algorithms.community.label_propagation_communities(self.graph)

            if method.startswith("mod"):
                comm=nx.algorithms.community.greedy_modularity_communities(self.graph)

            if method.startswith("async"):
                try:
                    comm = nx.algorithms.community.asyn_fluidc(self.graph,k=k,max_iter=iter)
                except:
                    tools.progress(100,100,"Impossible d'exécuter async_fluid")


            i=0
            for c in comm:
                cl=cluster(prefixe+str(i),index=list(c),color=draw.colors[i % len(draw.colors)])
                i=i+1
                tools.progress(i, 100, "Fabrication des clusters")
                self.clusters.append(cl)

            tools.progress(100, 100, "Clustering terminé")
            self.save_cluster(self.url+"_"+method)

        else:
            tools.progress(100,100,"Chargement des clusters")

    def print_properties(self):
        rc:dict=dict()
        rc["Nodes"]=str(len(self.graph.nodes))
        rc["Edges"]=str(len(self.graph.edges))
        #rc["local efficiency"]=nx.local_efficiency(self.graph)
        #rc["global efficiency"]=nx.global_efficiency(self.graph)
        return pd.DataFrame.from_dict(rc,orient="index")

    def initByCluster(self):
        for c in self.clusters:
            self.graph.add_node(c.index,self.mesures()[c.index])
            for n1 in c.index:
                for n2 in c.index:
                    self.graph.add_edge(n1,n2)

    def initByDistance(self, seuil=1):
        self.init_distances()
        l_edges=[]
        for i in range(0,len(self.distances)):
            tools.progress(i,len(self.distances),"Construction du graphe")

            for j in range(0, len(self.distances)):
                if self.distances[i,j]<seuil:
                    l_edges.append([i,j])

        self.graph.add_edges_from(l_edges)
        d:dict=dict(zip(range(0,len(self.data)),self.data[self.name_col]))
        nx.set_node_attributes(self.graph,d , "label")
        nx.set_node_attributes(self.graph, self.data[self.measures_col],self.measures_col)


