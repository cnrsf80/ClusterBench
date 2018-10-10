import copy
from clusterBench import tools
import datetime
import pandas as pd
import clusterBench.algo as algo


def create_reference_model(data, col_name,n_mesures):
    print(str(len(data))+" mesures à traiter")
    print("Colonne de utilisé pour le nom "+col_name)

    data["Ref"] = data.index
    data.index = range(len(data))
    mod = algo.model(data, col_name, range(1, n_mesures))

    #Usage d'une autre fonction de distance que la distance euclidienne
    #mod.init_distances(lambda i, j: scipy.spatial.distance.cityblock(i, j))

    true_labels = mod.ideal_matrix()  # Définition d'un clustering de référence pour les métriques
    mod.clusters_from_labels(true_labels)
    return mod


class simulation:
    models=[]

    def __init__(self,model:algo.model,col_name:str):
        self.ref_model:algo.model=model
        self.col_name :str= col_name


    def convertParams(self,ps):
        ps["sup"]=[None]
        ps["sup2"]=[None]

        rc=[]
        keys=list(ps.keys())

        for i in range(0,len(ps[keys[0]])):
            for j in range(0, len(ps[keys[1]])):
                for k in range(0, len(ps[keys[2]])):
                    c1=ps[keys[0]][i]
                    c2=ps[keys[1]][j]
                    c3=ps[keys[2]][k]
                    if c3 is None:
                        rc.append({keys[0]: c1, keys[1]: c2})
                    else:
                        rc.append({keys[0]:c1,keys[1]:c2,keys[2]:c3})
        return rc

    def execute(self,algo_name,url,func,ps:dict):
        print("Traitement de "+algo_name+" ********************************************************************")
        for p in self.convertParams(ps):
            m: algo.model=algo.model(self.ref_model.data,self.ref_model.name_col,self.ref_model.mesures_col)
            m=m.execute(algo_name,url, func,p)
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
            tools.progress(r,len(rc))
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
        print("Tracés 3D et 2D des résultats.")
        name = name.replace(" ", "_")
        code = "Calcul du " + str(datetime.datetime.now()) + "\n\n"
        for i in range(0, min(limit,len(self.models))):
            tools.progress(i,min(limit,len(self.models)))
            code = code + "\nPosition " + str(i + 1) + "<br>"
            code = code + self.models[i].trace("./saved", name + str(i), self.col_name, url)
            if withPerf:code = code + self.models[i].print_perfs()

        tools.create_html("index_" + name, code, url)



    def init_metrics(self, true_labels,showProgress=False):
        rc=""
        self.metrics: pd.DataFrame = pd.DataFrame()
        print("Calcul des métriques")
        print("Première passe\n")
        for i in range(len(self.models)):
            if showProgress:tools.progress(i, len(self.models))
            m:algo.model=self.models[i]
            m.init_metrics(true_labels)

        print("Tri des "+str(len(self.models))+" modeles")
        self.models.sort(key=lambda x: x.score, reverse=True)

        print("2eme passe\n")
        for i in range(len(self.models)):
            if showProgress:tools.progress(i, len(self.models))
            m = self.models[i]
            self.metrics = self.metrics.append(m.toDataframe(true_labels))
            rc=rc+m.print_perfs()

        return rc

    # def create_synthese_file(self,filename="synthese.xlsx"):
    #     writer = pd.ExcelWriter("./metrics/" + filename)
    #     self.metrics.to_excel(writer)
    #     writer.save()


    def print_infos(self):
        return str(len(self.models))+" modeles calculés"