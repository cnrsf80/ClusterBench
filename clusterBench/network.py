import base64
import os
import clusterBench.tools as tools
from clusterBench import draw
import networkx as nx
import pandas as pd
from clusterBench.cluster import cluster
from clusterBench.algo import model

#Representation d'un graphe
class network(model):
    graph=None
    positions=None

    # def __init__(self,nodes,edges):
    #     self.graph=nx.Graph()
    #     self.graph.add_node(nodes)
    #     self.graph.add_edge(edges)

    def __init__(self,url:str,algo_loc:str=""):
        self.clusters.clear()
        tools.progress(0,100,"Chargement du graphe")
        if not self.load(url,algo_loc):
            self.graph = nx.convert_node_labels_to_integers(self.graph, label_attribute="name")

        tools.progress(90,100,"Préparation")
        self.data: pd.DataFrame = pd.DataFrame(index=list(range(0,len(self.graph.nodes))))
        self.data["name"] = nx.get_node_attributes(self.graph,"name")

        self.dimensions = 3
        self.name_col = "name"


    # Positionnement des noeuds du graphe suivant l'algorithme gn,modularity,circular
    def relocate(self,dim=3,scale=3,method="spectral"):
        if method == "circular": d = nx.circular_layout(self.graph, scale=2, dim=3)
        if method=="spectral":d=nx.spectral_layout(self.graph,dim=dim,scale=scale)
        if method=="fr":d=nx.fruchterman_reingold_layout(self.graph,iterations=50,dim=3)
        i=1
        pos=[]
        for n in self.graph.nodes:
            if method=="fr" or method=="circular":
                pos.append(str(list(d.get(i-1))))
            else:
                pos.append(str(list(d.get(str(i)))))
            i = i + 1

        nx.set_node_attributes(self.graph, pos, "location")

        self.position=list(d.values())
        return d


    def save(self):
        path="./clustering/"+self.url+".gpickle"
        nx.write_gpickle(self.graph,path)


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
            if not url.startswith("http"): url = "./datas/" + url

            if url.endswith(".gml") or url.endswith(".graphml") :
                tools.progress(50, 100, "Chargement du fichier au format GML")
                try:
                    self.graph =nx.read_gml(url)
                except:
                    self.graph=nx.read_graphml(url)

            if url.endswith(".gexf") or url.endswith(".gephi"):
                try:
                    self.graph = nx.read_gexf(url)
                except:
                    print("Impossible de lire "+url)


            if self.graph is None:
                tools.progress(50, 100, "Chargement depuis la matrice de distance")
                self.data: pd.DataFrame = tools.get_data_from_url(url)
                if not self.data is None:
                    self.create_graph_from_dataframe()
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


    def findClusters(self,prefixe="cl_",method="gn",number_of_comm=5):
        if not self.load_cluster(self.url+"_"+method+str(number_of_comm)):
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
                    comm = nx.algorithms.community.asyn_fluidc(self.graph,k=number_of_comm)
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
