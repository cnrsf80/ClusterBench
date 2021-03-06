from clusterBench import draw
import datetime
import pandas as pd
import clusterBench.algo as algo
import copy
import clusterBench.tools as tools
from sklearn import cluster as cl
import hdbscan
from collections import Counter
import stringdist

from flask import request

class simulation:

    models=[]

    #Créer la colonne de cluster de reference en fonction des noms des mesures
    #Utilisé par le constructeur
    def create_ref_cluster_from_name(self,data, label_col):
        rc = tools.tokenize(list(data[label_col]))
        return rc


    def __init__(self,data:pd.DataFrame,no_metric=False,format:dict=dict()):

        if draw.colors is None or len(draw.colors) < 2: draw.colors = draw.init_colors(200)
        self.data = data

        #Réglage des parametres
        if not "name" in format:
            format["name"]=[data.columns[0]]# Le libellé des mesures est pris sur la premiere colonne

        if not "measures" in format:
            format["measures"]=data.columns[range(1,len(data.columns.values))]

        if not "properties" in format:
            format["properties"]=[]

        # if not "properties" in format:
        #     #Par defaut les propriétées sont entre les mesures et l'index
        #     if int(format["name"])+1<min(list(format["measures"]))-1:
        #         format["properties"]=data.columns[list(range(format["name"]+1,min(format["measures"])-1))]
        #     else:
        #         format["properties"]=[]

        self.col_name = format["name"][0]
        self.col_measures=format["measures"]
        self.col_properties = format["properties"]

        i = 0
        for c in data[format["measures"]]:
            tools.progress(i, len(format["measures"]), "Conversion des chaines de caractères de " + c)
            i = i + 1
            if data[c].dtype == object and len(data[c]) > 0:
                l_values=set(data[c])
                items=dict(zip(l_values,[0]*len(l_values)))
                ref=data[c][1]

                if tools.getComplexity(data[c])>90:
                    data[c]=tools.tokenize(data[data.columns[i]])
                else:
                    for item in items.keys():
                        d=stringdist.levenshtein(item, ref)
                        items[item]=d

                    if len(items)<100:
                        data[c]=data[c].replace(items.keys(),items.values())
                    else:
                        l=[]
                        for k in data[c]:
                            l.append(items[k])

                        data[c]=l



        if not "cluster" in list(self.data.columns):
            if not "cluster" in format:
                format["cluster"]=[self.col_name]

            self.data["ref_cluster"] = self.create_ref_cluster_from_name(self.data, format["cluster"][0])

        self.dimensions = len(format["measures"])  # Les composantes sont les colonnes suivantes

        self.ref_model: algo.model = self.init_reference_model()
        if not no_metric:
            self.ref_model.init_metrics(self.ref_model.cluster_toarray())


    # Fonction principale d'exécution des algorithmes de clustering
    # retourne le code HTML résultat de l'éxécution des algorithmes
    def run_algo(self,params: str, name_algo: str):

        self.raz()

        if name_algo.upper().__contains__("HDBSCAN"):
            parameters = tools.buildDict(params, {"min_samples": [3], "min_cluster_size": [2], "alpha": [0.5]})
            self.execute(algo_name="HDBSCAN",
                        url="https://hdbscan.readthedocs.io/en/latest/how_hdbscan_works.html",
                        func=lambda x:
                            hdbscan.HDBSCAN(min_cluster_size=x["min_cluster_size"],
                                            min_samples=x["min_samples"],
                                            alpha=x["alpha"]),
                        ps=parameters,colors=draw.colors,useCache=True)

        if name_algo.upper().__contains__("MEANSHIFT"):
            parameters = tools.buildDict(params, {"bandwidth": [2]})
            self.execute("MEANSHIFT",
                        "http://scikit-learn.org/stable/modules/generated/sklearn.cluster.MeanShift.html#sklearn.cluster.MeanShift",
                        lambda x:
                        cl.MeanShift(bandwidth=x["bandwidth"], bin_seeding=False, cluster_all=True),
                        parameters,draw.colors,useCache=True)

        if name_algo.upper().__contains__("HAC"):
            parameters = tools.buildDict(params, {"n_clusters": [12]})
            self.execute("HAC",
                        "http://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html#sklearn.cluster.AgglomerativeClustering",
                        lambda x:
                        cl.AgglomerativeClustering(n_clusters=x["n_clusters"]),
                        parameters,draw.colors,useCache=True
                        )

        if name_algo.upper().__contains__("NEURALGAS"):
            parameters = tools.buildDict(params, {"passes": [10], "distance_toremove": [60]})
            for passes in parameters.get("passes"):
                for distance_toremove_edge in parameters.get("distance_toremove_edge"):
                    m: algo.model = algo.create_cluster_from_neuralgasnetwork(
                        copy.deepcopy(self.ref_model).clear_clusters(),draw.colors,
                        a=0.5,
                        passes=passes,
                        distance_toremove_edge=distance_toremove_edge)
                    m.params = [passes, distance_toremove_edge, ""]
                    m.help = "https://github.com/AdrienGuille/GrowingNeuralGas"
                    self.append_modeles(m)

        if len(self.models)==0 or "NOTREATMENT" in name_algo.upper() or "NO" in name_algo.upper():
            m=copy.deepcopy(self.ref_model)
            m.params=params
            m.setname("NOTREATMENT")
            self.append_modeles(m)




    #Créé le modele de référence à partir des données
    def init_reference_model(self,ref_cluster:int=None):
        print(str(len(self.data)) + " mesures à traiter")
        print("Colonne de utilisé pour le nom " + self.col_name)

        self.data["Ref"] = self.data.index
        self.data.index = range(len(self.data))
        mod = algo.model(self.data, self.col_name, self.col_measures)

        # Usage d'une autre fonction de distance que la distance euclidienne
        # mod.init_distances(lambda i, j: scipy.spatial.distance.cityblock(i, j))

        true_labels = mod.ideal_matrix()  # Définition d'un clustering de référence pour les métriques
        mod.clusters_from_labels(true_labels,draw.colors)
        return mod


    def convertParams(self,ps):
        ps["sup"]=[None]
        ps["sup2"]=[None]
        ps["sup3"] = [None]

        rc=[]
        keys=list(ps.keys())

        for i in range(0,len(ps[keys[0]])):
            for j in range(0, len(ps[keys[1]])):
                for k in range(0, len(ps[keys[2]])):
                    for l in range(0, len(ps[keys[3]])):
                        c1=ps[keys[0]][i]
                        c2=ps[keys[1]][j]
                        c3=ps[keys[2]][k]
                        c4 = ps[keys[3]][l]
                        if c4 is None:
                            rc.append({keys[0]: c1, keys[1]: c2,keys[2]: c3})
                        else:
                            if c3 is None:
                                rc.append({keys[0]: c1, keys[1]: c2})
                            else:
                                rc.append({keys[0]:c1,keys[1]:c2,keys[2]:c3,keys[3]:c4})
        return rc



    def execute(self,algo_name,url,func,ps:dict,colors,useCache=False):
        print("Traitement de "+algo_name+" ********************************************************************")
        for p in self.convertParams(ps):
            m: algo.model=algo.model(self.ref_model.data,self.ref_model.name_col,self.col_measures)
            m=m.execute(algo_name,url, func,colors,p,useCache)
            m.init_noise_cluster()
            self.models.append(copy.copy(m))



    #Permet d'ajouter directement des modeles a la simulation (calculé ex-nihilo)
    def append_modeles(self, mod):
        self.models.append(mod)


    def find(self,start:str):
        rc=[]
        for m in self.models:
            if m.name.startswith(start):
                rc.append(m)
        return rc

    def getOccurenceCluster(self,models, filter=""):
        occurence = []
        list_clusters = []
        list_model = []
        list_algo = []
        list_composition=[]
        for m in models:
            if (len(filter) == 0 or m.type == filter):
                for c in m.clusters:
                    if list_clusters.__contains__(c):
                        k = list_clusters.index(c)
                        occurence[k] = occurence[k] + 1
                        list_model[k].append(m.name)
                        if not list_algo[k].__contains__(m.type): list_algo[k].append(m.type)
                    else:
                        list_clusters.append(c)
                        list_composition.append(c.print(self.ref_model.data,label_col=self.col_name,sep=" "))
                        occurence.append(1)
                        list_algo.append([m.type])
                        list_model.append([m.name])

        rc = pd.DataFrame(columns=["Occurence", "Cluster", "Model"])
        rc["Occurence"] = occurence
        rc["Composition"]=list_composition
        rc["Cluster"] = list_clusters
        rc["Model"] = list_model
        rc["Algos"] = list_algo

        rc = rc.sort_values("Occurence")

        return rc

    # Création des occurences retournés dans un dataFrame
    def create_occurence_file(self, filter=""):
        print("Construction de la matrice d'occurence par cluster\n")
        code = ""
        rc = self.getOccurenceCluster(self.models, filter)
        for r in range(len(rc)):
            tools.progress(r,len(rc)-1)
            code = code + "\n<h1>Cluster présent dans " + str(
                round(100 * rc["Occurence"][r])) + "% des algos</h1>"
            c = rc["Cluster"][r]
            code = code + c.print(self.ref_model.data, self.col_name) + "\n"
            code = code + "\n présent dans " + ",".join(rc["Model"][r]) + "\n"

        #print(tools.create_html("occurences", code, "http://f80.fr/cnrs"))

        dfOccurences = pd.DataFrame(
            data={"Cluster": rc["Cluster"], "Composition":rc["Composition"],"Model": rc["Model"], "Algos": rc["Algos"], "Occurence": rc["Occurence"]})
        l_items = list(set(self.ref_model.data[self.col_name].get_values()))

        for item in l_items:
            dfOccurences[item] = [0] * len(rc)
            print("\nTraitement de la mesure "+item)
            for i in range(len(rc)):
                tools.progress(i, len(rc))
                c = dfOccurences["Cluster"][i]
                dfOccurences[item][i] = c.labels.count(item)

        return dfOccurences


    def create_trace(self, url="http://f80.fr/cnrs", name="best_",limit=10000,withPerf=False,):
        print("\nTracés 3D et 2D des résultats.")
        name = name.replace(" ", "_")
        code = "Calcul du " + str(datetime.datetime.now()) + "\n\n"
        for i in range(0, min(limit,len(self.models))):
            tools.progress(i,min(limit,len(self.models)))
            code = code + "\nPosition " + str(i + 1) + "<br>"
            code = code + self.models[i].trace("./saved", name + str(i), url)
            if withPerf:code = code + self.models[i].print_perfs()

        tools.create_html("index_" + name, code, url)



    #Evaluation des principales métriques du clustering obtenu pour une simulation
    def init_metrics(self,showProgress=False):
        rc=""
        self.metrics: pd.DataFrame = pd.DataFrame()
        print("Calcul des métriques")
        print("\nPremière passe")
        true_labels=self.ref_model.cluster_toarray()

        for i in range(len(self.models)):
            if showProgress:tools.progress(i, len(self.models))
            m:algo.model=self.models[i]
            m.init_metrics(true_labels)

        print("Tri des "+str(len(self.models))+" modeles")
        self.models.sort(key=lambda x: x.score, reverse=True)

        print("\n2eme passe")
        for i in range(len(self.models)):
            if showProgress:tools.progress(i, len(self.models))
            m = self.models[i]
            self.metrics = self.metrics.append(m.toDataframe(true_labels))
            rc=rc+m.print_perfs()

        return rc


    def print_infos(self):
        return str(len(self.models))+" modeles calculés"


    def get3d_html(self,n_pca=1,no_text=False,autorotate=False,add_property=False):
        code=""
        for i in range(0, len(self.models)):
            m:algo.model=self.models[i]

            if not no_text:code = code+m.table();

            props=[]
            if add_property:props=self.col_properties+list(self.col_measures)
            for pca_offset in range(0, n_pca):
                code = code + draw.trace_artefact_GL(m,
                                                     m.id+"_pca"+str(pca_offset),
                                                     m.name+" Axe="+str(pca_offset)+","+str(pca_offset+1)+","+str(pca_offset+2),
                                                     self.ref_model,
                                                     pca_offset,autorotate=autorotate,
                                                     add_property=props)

            if not no_text:code=code+"<br><br>"+m.print_perfs("<br>")

        return code



    def raz(self):
        self.models=[]

    def getLinks(self,data_source:str,param:str):
        rc=[]
        for m in self.models:
            rc.append("<a href='"+m.getLink("localhost",data_source,param,"5000")+"'>"+m.name+"</a>")
        return rc

    def synthese(self):
        code="Synthese des metriques:<br>"+self.metrics.to_html()
        return code
