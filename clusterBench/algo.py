from clusterBench.gng import GrowingNeuralGas
import os
import hashlib
import clusterBench.tools as tools
from clusterBench import draw
import time
from threading import Thread
import sklearn.metrics as metrics
import networkx as nx
import numpy as np
import pandas as pd
from networkx.algorithms import community
from clusterBench.tools import tirage,save


colors=[]
for i in range(200):colors.append(i)

#Représente un model
#un model est une liste de cluster après application d'un algorithme de clustering
class model:
    name=""
    id=""
    hash="" #code de hashage des données (utile pour le cache)
    delay:int=0 #delay en secondes
    silhouette_score:int=0
    score:int=0
    url=""
    url2d=""
    help=""
    rand_index = 0
    homogeneity_score = 0
    completeness_score = 0
    v_measure_score = 0
    data:pd.DataFrame=None
    dimensions:int=0

    def __init__(self, data,name_col,dimensions):
        #Thread.__init__(self)
        self.name_col=name_col
        self.clusters=[]
        self.dimensions=dimensions
        self.data=data
        s = ""
        for a in list(self.data.keys()): s = s + str(a)
        self.hash=hashlib.md5(s.encode()).hexdigest()


    #Calcul de la matrice de distance
    #func_distance est la fonction de calcul de la distance entre 2 mesures
    def init_distances(self,func_distance,force=False):
        print("Calcul de la matrice de distance")
        size=len(self.mesures())
        composition=self.mesures()

        namefile="./saved/matrix_distance_"+self.name
        if os.path.isfile(namefile+".npy") and force==False:
            self.distances=np.load(namefile+".npy")
        else:
            self.distances = np.asmatrix(np.zeros((len(composition.index), len(composition.index))))
            for i in range(size):
                print(size-i)
                for j in range(size):
                    if(self.distances[i,j]==0 and i!=j):
                        name_i=self.data[self.name_col][i]
                        name_j=self.data[self.name_col][j]
                        vecteur_i=composition.iloc[i].values
                        vecteur_j=composition.iloc[j].values
                        d=func_distance(vecteur_i,vecteur_j,name_i,name_j)
                        self.distances[i,j]=d
                        self.distances[j,i]=d

            np.save(namefile,self.distances)


    #Retourne la liste des composants par cluster
    def print_cluster(self,end_line=" - "):

        s="<h1>"+self.name+"</h1><h2>"+str(len(self.clusters))+" clusters trouvés</h2>"+end_line+end_line
        for c in self.clusters:
            s=s+c.print(self.data, self.name_col)+end_line
        return s

    #Mesure le temps de traitement de l'algorithme
    def start_treatment(self):
        self.delay=time.time()

    #Mesure le temps de traitement
    def end_treatment(self):
        self.delay=round((time.time()-self.delay)*10)/10


    #Produit une réprésentation 3D et une représentation 2D des mesures
    #après PCA et coloration en fonction du cluster d'appartenance
    def trace(self,path:str,filename,url_base=""):

        code=self.to3DHTML(0,False)

        save(code+"<br><h2>Composition des clusters</h2>"+self.print_cluster("<br><br>"),path + "/" + filename+self.name+ ".html")

        self.url= url_base +"/" + tools.normalize(filename+self.name) + ".html"
        #self.url2d = url_base + "/" + draw.trace_artefact_2d(self.mesures(), self.clusters, path, filename)

        s="<a href='"+self.url+"'>représentation 3D</a>\n"
        s= s + "<a href='" + self.url2d + "'>représentation 2D</a>\n"
        return s+"\n"

    #Convertis les clusters en un vecteur simple
    #la position désigne la mesure
    #le contenu désigne le numéro du cluster
    #format utilisé notamment pour les métriques
    def cluster_toarray(self):
        rc=np.zeros((len(self.data),),np.int)
        for k in range(len(self.clusters)):
            for i in self.clusters[k].index:
                rc[i]=k
        return rc

    #Enregistre le clustering dans un fichier au format binaire
    def save_cluster(self):
        if len(self.name)==0:return False
        res:np.ndarray=self.cluster_toarray()
        res.tofile("./clustering/"+self.hash+"_"+self.name+".array")
        return True

    #Charge le clustering depuis un fichier si celui-ci existe
    def load_cluster(self):
        try:
            res=np.fromfile("./clustering/"+self.hash+"_"+self.name+".array",np.int,-1)
            self.clusters_from_labels(res)
            return True
        except:
            return False


    def mesures(self):
        rc=list(self.data.columns)
        rc.remove(self.name_col)
        assert(self.dimensions>0)
        rc=rc[0:self.dimensions]
        mes=self.data[rc]
        return mes

    def toDataframe(self,labels_true=None):
        if self.score==0:
            self.init_metrics(labels_true=labels_true)

        obj={
            "Name":self.name,
            "Algo":self.type,
            "Param1":str(self.params[0]),
            "Param2":str(self.params[1]),
            "Param3":str(self.params[2]),
            "nClusters":len(self.clusters),
            "delay (secondes)":self.delay,
            "URL":self.url,
            "2D":self.url2d,
            "Help":self.help,
            "Clusters":self.print_cluster(),
            "Score":[self.score],
            "Rand_index":[self.rand_index],
            "Silhouette":[self.silhouette_score],
            "V-mesure":[self.v_measure_score]
        }

        v=self.cluster_toarray()
        for i in range(len(v)):
            obj[self.data[self.name_col][i]+"_"+str(i)]=v[i]

        rc=pd.DataFrame(data=obj)

        return rc


    def init_metrics(self,labels_true):
        if len(self.clusters)>2:
            labels=self.cluster_toarray()
            self.silhouette_score= metrics.silhouette_score(self.mesures(), labels)
            self.rand_index=metrics.adjusted_rand_score(labels_true, labels)

            #self.self.adjusted_mutual_info_score=metrics.self.adjusted_mutual_info_score(labels_true,labels)

            self.homogeneity_score=metrics.homogeneity_score(labels_true,labels)
            self.completeness_score=metrics.completeness_score(labels_true,labels)
            self.v_measure_score=metrics.v_measure_score(labels_true,labels)

            self.score=((self.silhouette_score+1)
                        +(self.rand_index+1)*1.5
                        +self.v_measure_score
                        )/6
            self.score=round(self.score*20*100)/100

        else:
            self.silhouette_score=0
            self.score=0
            self.rand_index=0
            self.homogeneity_score=0
            self.completeness_score=0
            self.v_measure_score=0

        return self.print_perfs()

    def print_perfs(self,endline="<br>"):
        s=("<h2>Algorithme : %s</h2>" % self.name)+endline
        s = s + ("Delay de traitement : %s sec" % self.delay) + endline
        s=s+("Nombre de clusters : %s" % len(self.clusters))+endline+endline

        if len(self.clusters)>1:
            s=s+"<a href='http://scikit-learn.org/stable/modules/classes.html#module-sklearn.metrics.cluster'>Indicateurs de performance du clustering</a>\n"
            s=s+("Silhouette score %s" % self.silhouette_score)+endline
            s=s+"Rand_index %s" % self.rand_index+endline
            #s=s+"Information mutuelle (https://fr.wikipedia.org/wiki/Information_mutuelle) : %s" % self.adjusted_mutual_info_score+"\n"
            s=s+"homogeneity_score %s" % self.homogeneity_score+endline
            s=s+"v_measure_score %s" % self.homogeneity_score+endline
            s=s+"completeness_score  %s" % self.completeness_score+endline

            s = s +("<h2>Score (silhouette sur 10 + rand,homogeneité, v_mesure et completness sur 2,5) <strong>%s / 20</strong></h2>" % self.score)
        return s


    def clusters_from_labels(self, labels,name="cl_"):
        n_clusters_ = round(max(labels) + 1)
        for i in range(n_clusters_):
            self.clusters.append(cluster(name + str(i), [], i,i))

        i = 0
        for l in labels:
            if l >= 0:
                self.clusters[l].add_index(i, self.data, self.name_col)
            i = i + 1


    def init_thread(self,algo_name,url,algo_func,p:dict):
        self.parameters=p
        self.algo_name = algo_name
        self.algo_func = algo_func
        self.url=url

    def run(self):
        self.execute(self.algo_name,self.url,self.algo_func,self.parameters)

    def clear_clusters(self):
        self.clusters=[]
        return self

    #Execution de l'algorithme passé en argument (argo) avec les paramétres (params)
    def execute(self,algo_name,url,algo,p:dict,useCache=False):
        name=algo_name+" "
        self.help=url
        self.params=[None]*3
        i=0
        for key in p.keys():
            value:str=str(p.get(key))
            if value.__contains__("000000000"):value=str(round(p.get(key)*100)/100)
            if(i<3):self.params[i] = str(value)
            i = i + 1
            name=name+key+"="+value+" "

        self.setname(name)
        self.id = hashlib.md5(name.encode()).hexdigest()

        if not useCache or not self.load_cluster():
            self.start_treatment()
            comp=None
            try:
                mes=self.mesures()
                func=algo(p)
                comp = func.fit(mes)
            except:
                print("Exécution de " + name + " en echec")
            finally:
                if not comp is None:
                    self.end_treatment()
                    self.clusters_from_labels(comp.labels_, algo_name)
                    print("Exécution de " + name + " Traitement " + str(self.delay) + " sec")
                    self.save_cluster()
        else:
            print("Chargement du cluster depuis un préenregistrement pour "+name)

        return self



    def ideal_matrix(self):
        print("Fabrication d'un cluster de référence pour les métriques")
        clusters=np.asarray(np.zeros(len(self.data)),np.int8)
        d:dict={}
        for k in range(len(self.data)):
            item=self.data[self.name_col][k]
            if d.get(item)==None:
                d[item] = [k]
            else:
                d[item].append(k)

        j=0
        for k in d.keys():
            for i in d.get(k):
                clusters[i]=j
            j=j+1

        return clusters

    def to3DHTML(self,pca_offset=0,for_jupyter=False,w="800px",h="800px"):
        if len(self.clusters)>0:
            return draw.trace_artefact_GL(self,"","")
            # return draw.trace_artefact_3d(self.mesures(), self.clusters,
            #                               title=self.name,
            #                               label_col=self.name_col,
            #                               for_jupyter=for_jupyter,
            #                               pca_offset=pca_offset,w=w,h=h)
        else:
            return "No cluster"


    def setname(self, name:str="ALGO"):
        self.name=name
        self.type=name.split(" ")[0]

    def clusters_from_real(self, data,name):
        if len(self.clusters)==0:
            pts=self.mesures().values
            labels=[0]*len(pts)
            for p in data:
                for i in range(len(pts)):
                    a=p[0]
                    b=pts[i]
                    if np.array_equal(a,b):
                        labels[i]=int(p[1])

            self.clusters_from_labels(labels,name)


#definie un cluster
class cluster:
    def __init__(self, name="",index=[],color="red",pos=0):
        self.index = index
        self.name = name
        self.color= draw.get_color(color)
        self.labels=[]
        self.position=pos
        self.marker=tirage(['^','o','v','<','>','x','D','*'])

    def contain(self,i):
        for n in self.index:
            if n == i:
                return True
        return False

    def add_index(self,index,data=None,label_col=""):
        self.index.append(index)
        if data is not None:
            col=data[label_col]
            self.labels.append(col[index])

    def print(self,data,label_col="",sep=" / "):
        s=("Cl:"+self.name+"=")
        s=s+(sep.join(data[label_col][self.index]))
        return s

    def __eq__(self, other):
        if set(other.index).issubset(self.index) and set(self.index).issubset(other.index):
            return True
        else:
            return False


def create_cluster_from_neuralgasnetwork(model:model,a=0.5,passes=80,distance_toremove_edge=8):
    data=model.mesures().values
    model.setname("NEURALGAS distance_toremove="+str(distance_toremove_edge)+" passes="+str(passes))

    if not model.load_cluster():
        print(model.name)
        model.start_treatment()
        gng = GrowingNeuralGas(data)
        gng.fit_network(e_b=0.05, e_n=0.006,
                        distance_toremove_edge=distance_toremove_edge,
                        modulo_affichage=10, a=a, d=0.995,
                        passes=passes, plot_evolution=False)
        model.end_treatment()
        print('Found %d clusters.' % gng.number_of_clusters())
        model.clusters_from_real(gng.cluster_data(), "NEURALGAS_")
        model.save_cluster()
    else:
        print("Chargement de "+model.name)

    return model


# def create_two_clusters(G:nx.Graph):
#     clusters = []
#     partition = community.kernighan_lin_bisection(G, None, 500, weight='weight')
#
#     i=0
#     for p in partition:
#         clusters.append(cluster("kernighan_lin - "+str(i),p))
#         i=i+1
#
#     return clusters


# def create_ncluster(G:nx.Graph,target=4):
#     clusters =[cluster("premier",G.nodes)]
#     print("Recherche des clusters")
#     backup_G=G.copy()
#     while len(clusters) < target:
#        #on cherche le plus grand cluster
#        print(target-len(clusters))
#        maxlen=0
#        k=-1
#        for i in range(0,len(clusters)):
#            if len(clusters[i].index)>maxlen:
#                maxlen=len(clusters[i].index)
#                k=i
#         #On divise en deux le plus grand cluster et on le supprime
#        G = backup_G.subgraph(clusters[k].index)
#        clusters.remove(clusters[k])
#        for c in create_two_clusters(G):clusters.append(c)
#
#     return clusters


def create_clusters_from_asyncfluid(G,n_community):
    coms = community.asyn_fluidc(G, n_community, 500)
    partition = []
    for c in coms:
        partition.append(cluster("asyncfluid",c))
    return partition


# import pyclustering.cluster.optics as OPTICS
# def create_cluster_from_optics(data, eps):
#     cl=OPTICS.optics(data,eps).get_clusters()
#     print(cl)