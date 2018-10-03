import copy
from clusterBench import tools
import datetime
import pandas as pd
import algo

def create_reference_model(data, col_name,n_mesures):
    data["Ref"] = data.index
    data.index = range(len(data))
    mod = algo.model(data, col_name, range(1, n_mesures))
    #mod.init_distances(lambda i, j: scipy.spatial.distance.cityblock(i, j))
    true_labels = mod.ideal_matrix()  # Définition d'un clustering de référence pour les métriques
    mod.clusters_from_labels(true_labels)
    return mod


class simulation:
    models=[]

    def __init__(self,model,col_name):
        self.ref_model=model
        self.col_name = col_name


    def convertParams(self,params):
        rc=[]
        keys=list(params.keys())
        for i in range(0,len(params[keys[0]])):
            for j in range(0, len(params[keys[1]])):
                c1=params[keys[0]][i]
                c2=params[keys[1]][j]
                rc.append({keys[0]:c1,keys[1]:c2})
        return rc

    def execute(self,algo_name,func,params:dict):
        print("Traitement de "+algo_name+" ********************************************************************")
        for param in self.convertParams(params):
            self.models.append(
                copy.deepcopy(self.ref_model).execute(algo_name, func,param)
            )


    def append_modeles(self, mod):
        self.models.append(mod)


    def getOccurenceCluster(self,models, filter=""):
        occurence = []
        list_clusters = []
        list_model = []
        list_algo = []
        for m in models:
            if (len(filter) == 0 or m.type == filter):
                for c in m.clusters:
                    if list_clusters.__contains__(c):
                        k = list_clusters.index(c)
                        occurence[k] = occurence[k] + 1
                        list_model[k].append(m.name)
                        if not list_algo[k].__contains__(m.type): list_algo[k].append(m.type)
                    else:
                        print("Ajout de " + c.name)
                        list_clusters.append(c)
                        occurence.append(1)
                        list_algo.append([m.type])
                        list_model.append([m.name])

        rc = pd.DataFrame(columns=["Occurence", "Cluster", "Model"])
        rc["Occurence"] = occurence
        rc["Cluster"] = list_clusters
        rc["Model"] = list_model
        rc["Algos"] = list_algo

        rc = rc.sort_values("Occurence")

        return rc

    # Création des occurences
    def create_occurence_file(self, name, filter=""):
        code = ""
        rc = self.getOccurenceCluster(self.models, filter)
        for r in range(len(rc)):
            code = code + "\n<h1>Cluster présent dans " + str(
                round(100 * rc["Occurence"][r])) + "% des algos</h1>"
            c = rc["Cluster"][r]
            code = code + c.print(self.ref_model.data, self.col_name) + "\n"
            code = code + "\n présent dans " + ",".join(rc["Model"][r]) + "\n"

        print(tools.create_html("occurences", code, "http://f80.fr/cnrs"))

        dfOccurences = pd.DataFrame(
            data={"Cluster": rc["Cluster"], "Model": rc["Model"], "Algos": rc["Algos"], "Occurence": rc["Occurence"]})
        l_items = list(set(self.ref_model.data[self.col_name].get_values()))

        for item in l_items:
            print(item)
            dfOccurences[item] = [0] * len(rc)
            for i in range(len(rc)):
                c = dfOccurences["Cluster"][i]
                dfOccurences[item][i] = c.labels.count(item)

        writer = pd.ExcelWriter("./saved/" + name + ".xlsx")
        dfOccurences.to_excel(writer, "Sheet1")
        writer.save()
        return (name)



    def create_trace(self, url="http://f80.fr/cnrs", name="best_",limit=10000):
        name = name.replace(" ", "_")
        code = "Calcul du " + str(datetime.datetime.now()) + "\n\n"
        for i in range(0, min(limit,len(self.models))):
            print("Trace du modele " + str(i))
            code = code + "\nPosition " + str(i + 1) + "<br>"
            code = code + self.models[i].trace("./saved", name + str(i), self.col_name, url)
            code = code + self.models[i].print_perfs()

        print(tools.create_html("index_" + name, code, url))



    def init_metrics(self, true_labels,showProgress=False):
        rc=""
        self.metrics: pd.DataFrame = pd.DataFrame()
        for i in range(len(self.models)):
            if showProgress:tools.progress(i, len(self.models))
            m=self.models[i]
            m.init_metrics(true_labels)

        self.models.sort(key=lambda x: x.score, reverse=True)

        for i in range(len(self.models)):
            if showProgress:tools.progress(i, len(self.models))
            m = self.models[i]
            self.metrics = self.metrics.append(m.toDataframe(true_labels))
            rc=rc+m.print_perfs()

        return rc

    def create_synthese_file(self,filename="synthese.xlsx"):
        writer = pd.ExcelWriter("./metrics/" + filename)
        self.metrics.to_excel(writer)
        writer.save()


    def print_infos(self):
        return str(len(self.models))+" modeles calculés"