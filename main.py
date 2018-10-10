

# def create_site_matrix(data,artefact_clusters):
#     sites=create_sites_df(data)
#     M = np.asmatrix(np.zeros((len(sites), len(sites))))
#     liste_sites = list(sites.Site)
#     for c in artefact_clusters:
#         for s_i in data.Site[c.index]:
#             for s_j in data.Site[c.index]:
#                 if s_i!=s_j:
#                     M[liste_sites.index(s_i),liste_sites.index(s_j)]=1
#                     M[liste_sites.index(s_j), liste_sites.index(s_i)] = 1
#
#     return M

import clusterBench.tools as tools

# models=create_gaussian_mixture_model(mes,params=np.arange(1,30))
# X=models[25].predict(data)
# exit(0)

#M0=create_matrix(data,0,"As (ppm)","Se (ppm)")
#M0:np.matrix=create_matrix(data,0,"Dim.1",lastColumn)
#plt.matshow(M0, cmap=plt.cm.Blues)
#plt.show()

#G0=nx.from_numpy_matrix(M0)

import pandas as pd
import clusterBench.simulation as simulation
import clusterBench.algo as algo
import copy

tools.mkdir("clustering")
tools.mkdir("metrics")
tools.mkdir("saved")
tools.mkdir("visualization")

print("Syntaxe: python3 main.py <Fichier excel a traiter> <colone de nom des mesures> <liste des algos a executer>")
print("Exemple : python3 main.py './datas/Pour clustering.xlsx' 'id' 'HAC,DBSCAN,BIRCH,MEANSHIFT,NEURALGAS,SPECTRAL'")

import sys
source_file="./datas/Pour clustering.xlsx"
if len(sys.argv)>1:source_file=sys.argv[1]

col_name="id"
if len(sys.argv)>2:col_name=sys.argv[2]

algos:list=["HAC","DBSCAN","BIRCH","MEANSHIFT","NEURALGAS","SPECTRAL"]
if len(sys.argv)>3:algos:list=sys.argv[3].split(",")

ref_mod=simulation.create_reference_model(pd.read_excel(source_file),col_name,11)
print(ref_mod.print_cluster("\n\n"))

import numpy as np
from sklearn import cluster as cl
# from sklearn.cluster import OPTICS

s= simulation.simulation(ref_mod, col_name)

# print("OPTICS")
# for eps in np.arange(0.3,0.9,0.1):
#     m:algo.modele=algo.create_cluster_from_optics(
#         copy.deepcopy(ref_mod).clear_clusters(),
#         eps=eps
#     )
#     m.params = [eps]
#     m.help = "https://github.com/annoviko/pyclustering/blob/master/pyclustering/cluster/optics.py"
#     s.append_modeles(m)


# import hdbscan
# s.execute("HDDBSCAN","hhttps://github.com/scikit-learn-contrib/hdbscan",
#           lambda x:
#             hdbscan.HDBSCAN(min_cluster_size=x['min_cluster_size']),
#           {"min_cluster_size":range(2,25)}
# )


if algos.__contains__("HAC"):
    s.execute("HAC","http://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html#sklearn.cluster.AgglomerativeClustering",
              lambda x:
                cl.AgglomerativeClustering(n_clusters=x["n_cluster"],affinity=x["method"]),
              {"n_cluster":range(10,25),"method":["euclidean"]}
              )

if algos.__contains__("DBSCAN"):
    s.execute("DBSCAN","http://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html",
            lambda x:
                cl.DBSCAN(eps=x["eps"], min_samples=x["min_elements"],leaf_size=x["leaf_size"],n_jobs=4),
            {"eps": np.arange(0.1, 0.9, 0.1), "min_elements": range(2, 6),"leaf_size":range(10,60,20)})

if algos.__contains__("BIRCH"):
    s.execute("BIRCH","http://scikit-learn.org/stable/modules/generated/sklearn.cluster.Birch.html#sklearn.cluster.Birch",
            lambda x:
                cl.Birch(threshold=x["threshold"], n_clusters=x["n_clusters"],branching_factor=x["branching_factor"]),
            {"threshold": np.arange(0.1, 0.6, 0.1), "n_clusters": range(2, 25),"branching_factor":range(20,80,20)})

if algos.__contains__("MEANSHIFT"):
    s.execute("MEANSHIFT","http://scikit-learn.org/stable/modules/generated/sklearn.cluster.MeanShift.html#sklearn.cluster.MeanShift",
                lambda x:
                    cl.MeanShift(bandwidth=x["bandwidth"],bin_seeding=False, cluster_all=True),
                {"bandwidth": np.arange(1,5,0.5)})

if algos.__contains__("SPECTRAL"):
    s.execute("SPECTRAL","http://scikit-learn.org/stable/modules/generated/sklearn.cluster.SpectralClustering.html#sklearn.cluster.SpectralClustering",
            lambda x: cl.SpectralClustering(n_clusters=x["n_cluster"],n_neighbors=x["n_neighbors"]),
            {"n_cluster": range(6,20), "n_neighbors": range(5,10)}
    )

if algos.__contains__("NEURALGAS"):
    for passes in range(10,250,30):
        for distance_toremove_edge in range(2,30,4):
            m:algo.model=algo.create_cluster_from_neuralgasnetwork(
                copy.deepcopy(ref_mod).clear_clusters(),
                passes=passes,
                distance_toremove_edge=distance_toremove_edge)
            m.params=[passes,distance_toremove_edge,""]
            m.help="https://github.com/AdrienGuille/GrowingNeuralGas"
            s.append_modeles(m)

import datetime



s.init_metrics(ref_mod.cluster_toarray(),True) #une première fois pour le tri

#post=str(datetime.datetime.now()).split(".")[0].replace(":","").replace("2018-","")
post=""

url_base="http://f80.fr/cnrs"
s.create_trace(url_base,"best"+post,300,False)
s.init_metrics(ref_mod.cluster_toarray(),True) #ajout des url de représentation

tools.save(s.metrics,"./metrics/synthese.xlsx",True)

print("Matrice d'occurence : "+url_base+"/"+tools.save(s.create_occurence_file(),"./saved/occurences.xlsx",True))
# print("Matrice d'occurence : "+url_base+"/"+tools.save(s.create_occurence_file(filter="BIRCH"),"occurencesBIRCH.xlsx"))
# print("Matrice d'occurence : "+url_base+"/"+tools.save(s.create_occurence_file(filter="NEURALGAS"),"occurencesNEURALGAS.xlsx"))


#artefact_clusters=create_ncluster(G0,8);
#artefact_clusters=create_clusters_from_girvannewman(G0);

#for c in artefact_clusters:c.print(data,"clusterBench label")

#trace_artefact(G0,artefact_clusters,data,"Ref")



# M=create_site_matrix(data,artefact_clusters)
# G=nx.from_numpy_matrix(M)
# sites_clusters=create_clusters_from_asyncfluid(G,4)

#Affichage
# for c in sites_clusters:c.print(data,"Site")
# trace_artefact(G,sites_clusters,data,"Site")


#https://python-visualization.github.io/folium/docs-v0.6.0/
#mymap=folium.Map(location=[48,2],zoom_start=13)
#draw_site_onmap(mymap,G,sites_clusters,create_sites_df(data),"map.html")

