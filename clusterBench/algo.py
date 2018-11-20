import itertools

from scipy.spatial.qhull import ConvexHull

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
import copy

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
    url=""
    url2d=""
    help=""
    rand_index = 0
    homogeneity_score = 0
    completeness_score = 0
    v_measure_score = 0
    data:pd.DataFrame=None
    dimensions:int=0
    clusters_distance:pd.DataFrame=None



    def __init__(self, data,name_col:str=None,dimensions:int=None,positions=None):

      self.name_col=name_col
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

    def getLink(self,domain:str,data_source:str,param:str):
        rc="http://"+domain+":5000/"
        rc=rc+self.type+"/"
        rc=rc+param
        rc=rc+data_source.encode()
        return rc

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
            self.init_distance_cluster()
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

    def names(self):
        rc=list(self.data[self.name_col])
        return rc

    def toDataframe(self,labels_true=None):
        if self.score==0:
            self.init_metrics(labels_true=labels_true)

        for i in range(3):
            if len(self.params)<4:
                self.params.append(None);

        obj={
            "Algo": self.type,
            "Name":self.name,
            "Param1":str(self.params[0]),
            "Param2":str(self.params[1]),
            "Param3":str(self.params[2]),
            "Param4":str(self.params[3]),
            "Nbr Clusters":len(self.clusters),
            "delay (secondes)":self.delay,
            "URL":self.url,
            "2D":self.url2d,
            "Help":self.help,
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

    #Initialise les metriques d'un model sur la base du clustering labels_true
    def init_metrics(self,labels_true):
        mes=self.mesures()
        for c in self.clusters:
            c.init_metrics(mes)

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


    def clusters_from_labels(self, labels,name="cl_"):
        n_clusters_ = round(max(labels) + 1)
        for i in range(n_clusters_):
            if i>=len(draw.colors):i=1
            color=draw.colors[i]
            c:cluster=cluster(name + str(i), [], color,i)
            self.clusters.append(c)

        i = 0
        for l in labels:
            if l >= 0:
                self.clusters[l].add_index(i, self.data, self.name_col)
            i = i + 1

        for c in copy.deepcopy(self.clusters):
            if len(c.index)==0:self.clusters.remove(c)

        for c in self.clusters:
            c.findBestName(self.data[self.name_col])

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
    def execute(self,algo_name,url,algo,p:dict,useCache=False):
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

        # d:dict={}
        # for k in range(len(self.data)):
        #     item=self.data[self.name_col][k]
        #     if d.get(item)==None:
        #         d[item] = [k]
        #     else:
        #         d[item].append(k)
        #
        # j=0
        # for k in d.keys():
        #     for i in d.get(k):
        #         clusters[i]=j
        #     j=j+1
        # return clusters

        return np.asarray(self.data["ref_cluster"],np.int8)



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


    def init_noise_cluster(self):
        noise=[]
        for i in range(len(self.data)):
            find=False
            for c in self.clusters:
                if c.index.__contains__(i):
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


#definie un cluster
class cluster:
    #initialisation d'un cluster vide
    def __init__(self, name="",index=[],color="red",pos=0):
        self.index = index
        self.name = name
        self.color= list(color)
        self.labels=[]
        self.position=pos
        self.clusters_distances=dict()  #Distance aux autres cluster
        self.center=None
        self.variance = None
        self.marker=tirage(['^','o','v','<','>','x','D','*'])

    def init_metrics(self,mes):
        pts:pd.DataFrame=mes.iloc[self.index]
        self.variance=np.var(pts.values)
        self.center=np.mean(pts.values)

    def distance_min(self,c,mes):
        d_min=np.inf
        for i1 in self.index:
            for i2 in c.index:
                v=mes[i1]-mes[i2]
                d=np.linalg.norm(v)
                if d<d_min:
                    d_min=d
                    save_i1=i1
                    save_i2=i2
        return d_min,save_i1,save_i2

    def contain(self,i):
        for n in self.index:
            if n == i:
                return True
        return False

    #Remplissage d'un cluster
    def add_index(self,index,data=None,label_col=""):
        self.index.append(index)
        if data is not None:
            col=data[label_col]
            self.labels.append(col[index])

    #Initialisation de l'enveloppe d'un cluster
    from scipy.spatial import ConvexHull
    def get_3dhull(self,data,offset):
        facets = []
        pts = data[self.index]

        if(len(pts)>3):
            try:
                hull=ConvexHull(pts)
            except:
                return facets

            for p in hull.simplices:
                k:list=list(p)
                facet=[self.name,offset,self.color,list(pts[k[0]]),list(pts[k[1]]),list(pts[k[2]])]
                facets.append(facet)

        if len(pts)==3:
            facet = [self.name, offset,self.color,list(pts[0]), list(pts[1]), list(pts[2])]
            facets.append(facet)

        return facets


    def near_cluster(self):
        if self.clusters_distances is None:return ""
        d_min=np.inf
        rc=""
        for k in self.clusters_distances:
            if self.clusters_distances[k][0]<d_min:
                rc=k
                d_min=self.clusters_distances[k][0]
        return rc

    #Sortie texte du cluster
    def print(self,data,label_col="",sep=" / "):
        s=("Cl:"+self.name+"=")
        s=s+(sep.join(data[label_col][self.index]))
        return s

    #sortie destinée à un tableau html
    def td(self,data,label_col=""):
        rgb:str="rgb("+str(self.color[0]*255)+","+str(self.color[1]*255)+","+str(self.color[2]*255)+")"
        s=("<td style='background-color:"+rgb+"'><strong>"+self.name+"&nbsp;&nbsp;</strong></td>")
        s = s + "<td>"+str(len(self.index))+"</td><td>"
        s=s+self.near_cluster()+"</td><td>"
        s=s+("</td><td>".join(data[label_col][self.index]))
        return s+"</td>"


    def __eq__(self, other):
        if set(other.index).issubset(self.index) and set(self.index).issubset(other.index):
            return True
        else:
            return False

    def findBestName(self, labels,prefixe="cl_"):
        rc=""
        for m in labels[self.index]:
            if len(m)>10:
                lib=str(m)[:10]
            else:
                lib=str(m)
            lib=str.replace(lib," ","")
            if not rc.__contains__(lib):rc=rc+lib+" "

        if len(rc)>50:rc=hashlib.md5(bytes(rc,"utf-8")).hexdigest()
        self.name=prefixe+str.strip(rc)


class network(model):
    graph=None
    positions=None

    # def __init__(self,nodes,edges):
    #     self.graph=nx.Graph()
    #     self.graph.add_node(nodes)
    #     self.graph.add_edge(edges)

    def __init__(self,url:str):
        self.graph=nx.read_gml(url)

        pos=self.relocate()
        self.data: pd.DataFrame = pd.DataFrame(list(pos.values()))

        self.data["name"] = list(pos.keys())
        self.graph=nx.convert_node_labels_to_integers(self.graph)

        self.dimensions = 3
        self.name_col = "name"


    def relocate(self,dim=3,scale=3):
        if self.positions is None:
            d=nx.spectral_layout(self.graph,dim=dim,scale=scale)
            self.position=list(d.values())
            return d
        else:
            return self.positions


    def findClusters(self,prefixe="cl_"):
        comm=nx.algorithms.community.girvan_newman(self.graph)
        self.relocate()
        i=0

        for c in next(comm):
            cl=cluster(prefixe,index=list(c),color=draw.colors[i])
            i=i+1
            self.clusters.append(cl)






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