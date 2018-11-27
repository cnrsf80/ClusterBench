import sklearn.decomposition as decomp
import ezvis3d as v3d
import pandas as pd
import networkx as nx
from matplotlib import colors as mcolors
import clusterBench.tools as tools

import random


#Palette de couleurs
from clusterBench import algo


def color_distance(c1,c2):
    s=0
    for i in range(0,3):
        s=s+abs(c1[i]-c2[i])
    return s


colors=[[random.random(),random.random(),random.random()]]
for i in range(1,250):
    while True:
        new_color=[random.random(),random.random(),random.random()]
        b=True
        for k in range(0, i):
            if color_distance(colors[i-k-1],new_color)<0.2:b=False

        if b:
            colors.append(new_color)
            break


#Affichage des mesures en 2D
def trace_artefact_2d(data, clusters, path,name):
    pca = decomp.pca.PCA(n_components=2)
    pca.fit(data)
    newdata = pca.transform(data)

    for c in clusters:
        plt.scatter(x=newdata[c.index,0],y=newdata[c.index,1],c=[c.color],marker=c.marker,label=c.name,alpha=0.3)

    plt.legend(title_fontsize="xx-small", bbox_to_anchor=(0.95, 1), loc=2, borderaxespad=0.)
    plt.savefig(path+"/"+name+".png",dpi=400)
    plt.clf()

    return name+".png"


# def trace_spectre(model,X):
#     reachability = model.reachability_[model.ordering_]
#     labels = model.labels_[model.ordering_]
#
#     space = numpy.arange(len(X))
#
#     for k, c in zip(range(0, 5), colors):
#         Xk = space[labels == k]
#         Rk = reachability[labels == k]
#         plt.plot(Xk, Rk, c, alpha=0.3)
#
#     plt.plot(space[labels == -1], reachability[labels == -1], 'k.', alpha=0.3)
#     plt.set_ylabel('Reachability (epsilon distance)')
#     plt.set_title('Reachability Plot')


from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt


def drawOnPlot_3D(points,lines):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for p in points:
        ax.scatter(p[0],p[1],p[2],c="r",marker="o")


#Production des fichiers HTML de représentation en 3d dynamique des mesures avec coloration par cluster
def draw_3D(li_data,for_jupyter=False,lines=None,w="800px",h="800px"):
    df_data = pd.DataFrame(li_data)

    g = v3d.Vis3d()
    g.width = w
    g.height = h
    g.style = 'dot-color'
    g.tooltip = """function (point) {
        var dt=window.dta;
        return '<b>' + point.data.label + '</b>';
    }"""

    g.showPerspective = True
    g.showLegend=False
    g.showXAxis = False
    g.showYAxis = False
    g.showZAxis = False
    g.showGrid = True
    g.keepAspectRatio = True
    g.verticalRatio = 1.0

    g.cameraPosition = {'horizontal':-0.54,'vertical':0.5,'distance':2}
    g.plot(df_data)

    if not lines == None:
        df_line = pd.DataFrame(lines)
        #g.style="line"
        #g.plot(df_line)

    code= g.html(df_data, center=for_jupyter,save=False, notebook=for_jupyter, dated=True)

    return code


# def draw_with_babylon(li_data,for_jupyter=False,lines=None,w="800px",h="800px"):
#     df_data = pd.DataFrame(li_data)

#Projection 3D des cluster et cluster de référence + calcul des enveloppes
def pca_totrace(mod:algo.model,ref_cluster,properties_dict:list,pca_offset=0):
    labels=mod.names()
    mesures=tools.normalize(mod.mesures())

    pca: decomp.pca.PCA = decomp.pca.PCA(n_components=3 + pca_offset)
    pca.fit(mesures)
    newdata = pca.transform(mesures)

    li_data:list = []
    facets=[]

    i=0
    for c in mod.clusters:
        i = i + 1
        tools.progress(i,len(mod.clusters),"Préparation des clusters")
        if len(c.clusters_distances)>0:
            distances: pd.DataFrame = pd.DataFrame.from_dict(c.clusters_distances,orient="index",columns=["distance","p1","p2"])
            distances=distances.sort_values("distance")
            distances=distances[0:10]
            distances=distances.transpose()
            ss=distances.to_json()
        else:
            ss="{}"
        #distances.sort_index(ascending=False)

        facets.append(c.get_3dhull(newdata,pca_offset))

        for k in range(len(c.index)):
            ind=c.index[k]
            x=newdata[ind, pca_offset]
            y=newdata[ind, pca_offset + 1]
            z=newdata[ind, pca_offset + 2]
            sp={
                'index':ind,
                'x': x,
                'y': y,
                'z': z,
                'style': c.color,
                'label': labels[ind],
                'name': labels[ind],
                'size':1,
                'form':'sphere',
                'cluster': c.name,
                'ref_cluster':ref_cluster[ind],
                'cluster_distance':ss
            }
            li_data.append(sp)

    for i in range(0,len(li_data)):
        tools.progress(i,len(li_data),"Ajout des propriétés")
        row=li_data[i]["index"]
        d:dict=properties_dict[row-1]
        li_data[i]=({**li_data[i], **d})

    return li_data,facets

#Representation 3d du graph
def to3D(G:algo.network,positions=None):
    li_data=[]
    for c in G.clusters:
        for p in c.index:
            if positions is None:
                row=G.data.iloc[[p]]
            else:
                row=positions[p]

            sp={
                'x':float(row[0]),'y':float(row[1]),'z':float(row[2]),
                'label':G.data[G.name_col][p],
                'name':G.data[G.name_col][p],
                'style':c.color,
                'cluster':c.name,
                'form': 'sphere'
            }
            n=G.graph.nodes[p]
            li_data.append({**sp,**n})

    edges=[]
    for e in G.graph.edges:
        edges.append({"start":e[0],"end":e[1]})

    return li_data,edges


#Production des fichiers HTML de représentation en 3d dynamique des mesures avec coloration par cluster
def trace_artefact_3d(data, clusters, ref_cluster,title="",label_col="",for_jupyter=False,pca_offset=0,w="800px",h="800px"):
    #TODO: a corriger
    # li_data=pca_totrace(data,clusters,[],pca_offset,ref_cluster)
    # code=""
    # if len(title)>0:code="<h1>"+title+"</h1>"
    # code=code+"<h3>Réprésentation 3d sur les axes "+str(pca_offset)+","+str(pca_offset+1)+","+str(pca_offset+2)+"</h3>"
    # return code+draw_3D(li_data,for_jupyter=for_jupyter,lines=None,w=w,h=h)
    pass



def trace_artefact(G, clusters):
    pos = nx.spectral_layout(G, scale=5, dim=len(clusters))
    # pos=nx.spring_layout(G,iterations=500,dim=len(clusters))
    # nx.set_node_attributes(G,"name")

    if len(clusters) > 0:
        i = 0
        labels = {}
        for c in clusters:
            # for k in c.index:
            #     G.nodes[k].name = data[label_col][k]
            #     labels[G.nodes[k]]=G.nodes[k]

            nx.draw_networkx_nodes(G,
                                   pos=pos,
                                   nodelist=c.index,
                                   alpha=0.6, node_size=200, node_color=c.color)

            i = i + 1

        # nx.draw_networkx_labels(G, pos, labels=labels,font_size=10, font_family='sans-serif')

        # nx.draw_networkx_edges(G, pos, alpha=0.5)
    else:
      nx.draw(G)

    plt.axis('off')
    # plt.savefig('graph.pdf', format="pdf")
    plt.show()


from flask import render_template

def create_dict_for_properties(data:pd.DataFrame):
    rc=[]
    names = data.columns.values
    for row in range(1,len(data)):
        values=data.iloc[[row]].values[0]
        d=dict(zip(names,values))
        #d=tmp.to_dict(orient="index")[row]
        rc.append(d)

    return rc

#Production du fichier à destination du tracé 3d
def trace_artefact_GL(mod:algo,id="",title="",ref_model:algo=None,pca_offset=0,autorotate="false"):

    properties_dict=create_dict_for_properties(mod.data)
    li_data,facets= pca_totrace(mod,mod.data['ref_cluster'],properties_dict,pca_offset)

    if ref_model is None:
        facets_ref=[]
    else:
        tmp_li_data,facets_ref=pca_totrace(ref_model,ref_model.data['ref_cluster'],properties_dict,pca_offset)

    d=pd.concat([mod.data.ix[:,0],mod.mesures()],axis=1,sort=False)

    toList=[]
    for line in d.values:
        toList.append(list(line))

    code=render_template("modele.html",
                         title=title,
                         name_zone="zone"+id,
                         datas=li_data,
                         autorotate=autorotate,
                         data_source=toList,
                         facets_ref=facets_ref,
                         facets=facets,
                         edges=[],
                         url_to_render="/static/rendering/render.html?offset="+str(pca_offset))
    return code

def trace_graph(G:algo.network,positions=None,autorotate=False):
    li_data,edges=to3D(G,positions)
    code = render_template("modele.html",
                           title="",
                           autorotate=autorotate,
                           name_zone="zone",
                           datas=li_data,
                           data_source=[],
                           facets_ref=[],
                           facets=[],
                           edges=edges,
                           url_to_render="/static/rendering/render.html")
    return code