import copy
import datetime
import numpy as np
import pandas as pd
import sklearn as sk

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



#data = pd.read_excel("cnx013_supp_table_s1.xlsx").head(200)

#data = pd.read_excel("ACP_article.xlsx")
#col_name="Nom article"
#n_mesures=19

#tools.clear_dir()

col_name="id"



# models=create_gaussian_mixture_model(mes,params=np.arange(1,30))
# X=models[25].predict(data)
# exit(0)

#M0=create_matrix(data,0,"As (ppm)","Se (ppm)")
#M0:np.matrix=create_matrix(data,0,"Dim.1",lastColumn)
#plt.matshow(M0, cmap=plt.cm.Blues)
#plt.show()

#G0=nx.from_numpy_matrix(M0)

def create_reference_model(data, col_name,n_mesures):
    data["Ref"] = data.index
    data.index = range(len(data))
    mod = algo.model(data, col_name, range(1, n_mesures))
    #mod.init_distances(lambda i, j: scipy.spatial.distance.cityblock(i, j))
    reference = algo.model(data, col_name)
    reference.clusters_from_labels(true_labels)


ref_mod=create_reference_model(pd.read_excel("Pour clustering.xlsx"),"id",11)
true_labels = ref_mod.ideal_matrix() #Définition d'un clustering de référence pour les métriques
ref_mod.print_cluster("\n")

from clusterBench import simulation, algo

s= simulation.simulation(ref_mod, col_name)
s.execute("HAC_eur",
          lambda x:
            sk.cluster.AgglomerativeClustering(n_clusters=x["n_cluster"],affinity=x["method"]),
          {"n_cluster":range(10,25),"method":["euclidean"]}
          )

s.execute("DBSCAN",
            lambda x:
                sk.cluster.DBSCAN(eps=x["eps"], min_samples=x["min_elements"], n_jobs=4),
            {"eps": np.arange(0.1, 0.9, 0.1), "min_elements": range(2, 6)})

s.execute("MEANSHIFT",
                lambda x:
                    sk.cluster.MeanShift(bandwidth=x["bandwidth"],min_bin_freq=x["min_bin_freq"]),
                {"bandwidth": np.arange(0.1,0.9,0.1), "min_bin_freq": range(1,4)})

s.execute("SPECTRALCLUSTERING",
            lambda x: sk.cluster.SpectralClustering(n_clusters=x["n_cluster"],n_neighbors=x["n_neighbors"]),
            {"n_cluster": range(6,20), "n_neighbors": range(5,10)}
)

s.execute("OPTICS",
            lambda x:
                sk.cluster.OPTICS(maxima_ratio=x["maxima_ratio"],
                      rejection_ratio=x["rejection_ratio"], min_samples=3,
                      n_jobs=-1),
    {"maxima_ratio": np.arange(0.3,0.9,0.1), "rejection_ratio": np.arange(0.3,0.8,0.1)}
)


print("Neural Gas network************************************************************************************************")
for passes in range(10,90,20):
    for distance_toremove_edge in range(6,38,4):
        s.append_modeles(algo.create_cluster_from_neuralgasnetwork(
            copy.deepcopy(ref_mod),
            passes=passes,
            distance_toremove_edge=distance_toremove_edge)
        )


url_base="http://f80.fr/cnrs"
name=str(datetime.datetime.now()).split(".")[0].replace(":","").replace("2018-","")

s.create_trace(url_base,"best"+name)
s.init_metrics(true_labels)
print(s.print_infos())

print("Matrice d'occurence : "+url_base+"/"+s.create_occurence_file("occurencesOPTICS",filter="OPTICS")+".html")
print("Matrice d'occurence : "+url_base+"/"+s.create_occurence_file("occurencesNEURALGAS",filter="NEURALGAS")+".html")

exit(0)

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

