from clusterBench.gng import GrowingNeuralGas
import os
import hashlib
import clusterBench.tools as tools
import time
import sklearn.metrics as metrics
import numpy as np
import pandas as pd
from clusterBench.cluster import cluster

#Représente un model
#un model est une liste de cluster après application d'un algorithme de clustering
class model:
    name=""
    id=""
    hash="" #code de hashage des données (utile pour le cache)
    delay:int=0 #delay en secondes
    silhouette_score:int=0
    score:int=0
    clusters=[]
    infos=dict()
    url=""
    url2d=""
    help=""
    rand_index = 0
    homogeneity_score = 0
    completeness_score = 0
    v_measure_score = 0
    data:pd.DataFrame=None
    dimensions:int=0
    measures_col:list=[]
    clusters_distance:pd.DataFrame=None

    def __init__(self,data,name_col:str,measures_col:list,positions=None):
      self.name_col=name_col
      self.dimensions=len(measures_col)
      self.measures_col=measures_col
      self.data=data
      self.clusters=[]
      self.hash=self.create_signature()


    def create_signature(self):
        s = ""
        for a in list(self.data.keys()):
            s = s + str(a)

        for c in self.data.columns:
            try:
                s=s+str(sum(self.data[c]))+"_"
            except:
                pass

        return hashlib.md5(s.encode()).hexdigest()


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

    #calcul la distance entre les clusters
    def init_distance_cluster(self):
        m=self.mesures().values
        i=0

        for c1 in self.clusters:
            tools.progress(i,len(self.clusters))
            i=i+1
            for c2 in self.clusters:
                if c1!=c2:
                    if c1.clusters_distances.get(c2.name) is None:
                        d=list(c1.distance_min(c2, m))
                        c1.clusters_distances[c2.name]=d
                        #c2.clusters_distances[c1.name]=d



    def init_matrice_distance_cluster(self):
        print("Calcul de la matrice de distance")
        if self.clusters_distance is None:
            self.clusters_distance = pd.DataFrame(index=self.get_cluster_names(), columns=self.get_cluster_names())

        for c1 in self.clusters:
            self.clusters_distance[c1.name][c1.name] = 0
            for c2 in c1.clusters_distances:
                d=c1.clusters_distances[c2][0]
                self.clusters_distance[c1.name][c2] = d
                self.clusters_distance[c2][c1.name] = d

        return self.clusters_distance


    def get_cluster_names(self):
        rc=[]
        for c in self.clusters:
            rc.append(c.name)
        return rc

    #Retourne la liste des composants par cluster
    def print_cluster(self,end_line=" - "):
        s="<h1>"+self.name+"</h1><h2>"+str(len(self.clusters))+" clusters trouvés</h2>"+end_line+end_line
        for c in self.clusters:
            s=s+c.print(self.data, self.name_col)+end_line
        return s

    def table(self):
        s="<h1>"+self.name+"</h1><h2>"+str(len(self.clusters))+" clusters trouvés</h2><table>"
        s=s+"<tr><td>Cluster Name</td><td>Eléments</td><td>Plus proche</td></tr>"
        for c in self.clusters:
            s=s+"<tr>"+c.td(self.data, self.name_col)+"</tr>"
        return s+"</table>"

    #Mesure le temps de traitement de l'algorithme
    def start_treatment(self):
        self.delay=time.time()

    #Mesure le temps de traitement
    def end_treatment(self):
        self.delay=round((time.time()-self.delay)*10)/10

    def getLink(self,domain:str,data_source:str,param:str,port="5000"):
        rc="http://"+domain+":"+port+"/"
        rc=rc+self.type+"/"
        rc=rc+param
        rc=rc+data_source.encode()
        return rc


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
    def save_cluster(self,result=None,filename=None):
        if result is None:
            res: np.ndarray = self.cluster_toarray()
        else:
            res: np.ndarray = result

        if filename is None:
            if len(self.name)==0:return False
            res.tofile("./clustering/"+self.hash+"_"+self.name+".array",sep=";")
        else:
            res.tofile("./clustering/"+filename+".array",sep=";")

        return res


    #Charge le clustering depuis un fichier si celui-ci existe
    def load_cluster(self,colors,filename=None):
        try:
            if filename is None:
                res=np.fromfile("./clustering/"+self.hash+"_"+self.name+".array",int,sep=";")
            else:
                res=np.fromfile("./clustering/"+filename+".array",int,sep=";")
            #self.init_distance_cluster()

            return np.array(list(res),dtype=int)
        except:
            return None


    def mesures(self):
        rc=self.data[self.measures_col]
        return rc

    def names(self):
        rc=list(self.data[self.name_col])
        return rc

    def toDataframe(self,labels_true=None):
        if self.score==0:
            self.init_metrics(labels_true=labels_true)

        for i in range(3):
            if len(self.params)<4:
                self.params.append(None);

        noise_cluster=self.clusters[len(self.clusters)-1]
        obj={
            "Algo": self.type,
            "Name":self.name,
            "Param1":str(self.params[0]),
            "Param2":str(self.params[1]),
            "Param3":str(self.params[2]),
            "Param4":str(self.params[3]),
            "Nbr Clusters":len(self.clusters),
            "Noise cluster size":len(noise_cluster.index),
            "Score":[self.score],
            "Rand_index":[self.rand_index],
            "Silhouette":[self.silhouette_score],
            "V-mesure":[self.v_measure_score],
            "Treatment delay (sec)": self.delay
        }

        v=self.cluster_toarray()
        for i in range(len(v)):
            obj[str(self.data[self.name_col][i])+"_"+str(i)]=v[i]

        rc=pd.DataFrame(data=obj)

        return rc

    #Initialise les metriques d'un model sur la base du clustering labels_true
    def init_metrics(self,labels_true):
        mes=self.mesures()
        i=0
        for c in self.clusters:
            tools.progress(i,len(self.clusters),"Initialisation des metrics des clusters")
            c.init_metrics(mes)
            i=i+1

        if len(self.clusters)>2:
            labels=self.cluster_toarray()
            tools.progress(10, 100, "Score de silhouete")
            self.silhouette_score= metrics.silhouette_score(self.mesures(), labels)

            tools.progress(40, 100, "Rand Index")
            self.rand_index=metrics.adjusted_rand_score(labels_true, labels)

            #self.self.adjusted_mutual_info_score=metrics.self.adjusted_mutual_info_score(labels_true,labels)

            tools.progress(50, 100, "Homogénéité")
            self.homogeneity_score=metrics.homogeneity_score(labels_true,labels)

            tools.progress(60, 100, "Completeness")
            self.completeness_score=metrics.completeness_score(labels_true,labels)

            tools.progress(70, 100, "V-mesure")
            self.v_measure_score=metrics.v_measure_score(labels_true,labels)

            self.score=((self.silhouette_score+1)
                        +(self.rand_index+1)*1.5
                        +self.v_measure_score
                        )/6
            self.score=round(self.score*20*100)/100

            tools.progress(100, 100, "Calcul metriques terminé")
            if len(self.clusters)<3:
                self.init_distance_cluster()

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
            s=s+"<a href='http://scikit-learn.org/stable/modules/classes.html#module-sklearn.metrics.cluster'>Indicateurs de performance du clustering</a>"+endline
            s=s+("Silhouette score %s" % self.silhouette_score)+endline
            s=s+"Rand_index %s" % self.rand_index+endline
            #s=s+"Information mutuelle (https://fr.wikipedia.org/wiki/Information_mutuelle) : %s" % self.adjusted_mutual_info_score+"\n"
            s=s+"homogeneity_score %s" % self.homogeneity_score+endline
            s=s+"v_measure_score %s" % self.homogeneity_score+endline
            s=s+"completeness_score  %s" % self.completeness_score+endline

            s = s +("<h2>Score (silhouette sur 10 + rand,homogeneité, v_mesure et completness sur 2,5) <strong>%s / 20</strong></h2>" % self.score)
            if not self.clusters_distance is None:s = s + "Distance entre cluster:<br>" + self.clusters_distance.to_html() + "<br>"

        return s


    def clusters_from_labels(self, labels:np.ndarray,colors,name="cl_"):

        #offset=min(old_labels)+10000
        #labels=[x+offset for x in old_labels]

        d=dict()
        i = 0
        for l in labels:
            if not l in d.keys():d[l] = []
            d[l].append(i)
            i = i + 1

        i=0
        for k in d.keys():
            i=i+1
            tools.progress(i, len(d), "Construction des clusters");
            color=colors[i % len(colors)]
            if k!=-1:
                c:cluster=cluster(name + str(i),index=d[k], color=color,pos=i)
                c.findBestName(self.data[self.name_col], "cl" + str(i) + "_")
                self.clusters.append(c)

    # def init_thread(self,algo_name,url,algo_func,p:dict):
    #     self.parameters=p
    #     self.algo_name = algo_name
    #     self.algo_func = algo_func
    #     self.url=url

    def run(self):
        self.execute(self.algo_name,self.url,self.algo_func,self.parameters)

    def clear_clusters(self):
        self.clusters=[]
        return self

    #Execution de l'algorithme passé en argument (argo) avec les paramétres (params)
    def execute(self,algo_name,url,algo,colors,p:dict,useCache=False):
        name=algo_name+" "
        self.help=url
        self.params:list=[None]*6
        i=0
        for key in p.keys():
            value:str=str(p.get(key))
            if value.__contains__("000000000"):value=str(round(p.get(key)*100)/100)
            if(i<len(p.keys())):self.params[i] = str(value)
            i = i + 1
            name=name+key+"="+value+" "

        self.setname(name)
        self.id = hashlib.md5(name.encode()).hexdigest()

        r=None
        if useCache:r=self.load_cluster(colors)
        if r is None:
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
                    r=self.save_cluster(comp.labels_)
                    print("Exécution de " + name + " Traitement " + str(self.delay) + " sec")
        else:
            print("Chargement du cluster depuis un préenregistrement pour "+name)

        self.clusters_from_labels(r, colors, algo_name)

        return self



    def ideal_matrix(self):
        print("Fabrication d'un cluster de référence pour les métriques")
        #clusters=np.asarray(np.zeros(len(self.data)),np.int8)
        rc= np.asarray(self.data["ref_cluster"],np.int8)
        return rc



    def init_noise_cluster(self):
        noise=[]
        for i in range(len(self.data)):
            find=False
            for c in self.clusters:
                if i in c.index:
                    find=True
                    break
            if not find:
                noise.append(i)

        self.clusters.append(cluster("noise",noise,[0.8,0.8,0.8],len(self.clusters)))



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



def create_cluster_from_neuralgasnetwork(model:model,colors,a=0.5,passes=80,distance_toremove_edge=8):
    data=model.mesures().values
    model.setname("NEURALGAS distance_toremove="+str(distance_toremove_edge)+" passes="+str(passes))

    if not model.load_cluster(colors):
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
        print("Chargement du résultat de "+model.name+" depuis le cache")

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


# def create_clusters_from_asyncfluid(G,n_community=50):
#     coms = community.asyn_fluidc(G, k=n_community,max_iter=500)
#     partition = []
#     for c in coms:
#         partition.append(cluster("asyncfluid",c))
#     return partition


# import pyclustering.cluster.optics as OPTICS
# def create_cluster_from_optics(data, eps):
#     cl=OPTICS.optics(data,eps).get_clusters()
#     print(cl)