import hashlib
import numpy as np
import pandas as pd
from clusterBench.tools import tirage
from scipy.spatial import ConvexHull

#definie un cluster
class cluster:
    #initialisation d'un cluster vide
    def __init__(self, name="",index=[],color=[0.5,0.5,0.5],pos=0):
        self.index = index
        self.name = name
        self.color= color
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
                k=[]
                for i in list(p):k.append(self.index[i])
                facet=[self.name,offset,self.color,k]
                facets.append(facet)

        if len(pts)==3:
            facet = [self.name, offset,self.color,self.index]
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
        s=s+self.near_cluster()+"</td><td></td><td>"
        if len(self.index)>0:s=s+("<td>".join(data[label_col][self.index]))+"</td>"
        return s


    def __eq__(self, other):
        if set(other.index).issubset(self.index) and set(self.index).issubset(other.index):
            return True
        else:
            return False

    def findBestName(self, labels,prefixe="cl_"):
        rc=""
        for m in labels[self.index]:
            if len(str(m))>10:
                lib=str(m)[:10]
            else:
                lib=str(m)
            lib=str.replace(lib," ","")
            if not rc.__contains__(lib):rc=rc+lib+" "

        if len(rc)>40:
            if prefixe!="cl_":
                rc=rc[0:40]
            else:
                rc=hashlib.md5(bytes(rc,"utf-8")).hexdigest()

        self.name=prefixe+str.strip(rc)
