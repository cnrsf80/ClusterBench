import sklearn.decomposition as decomp
import ezvis3d as v3d
import pandas as pd
import networkx as nx
from matplotlib import colors as mcolors


#Palette de couleurs
def get_color(index):
    colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)
    return list(colors.values())[index]

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
    g.tooltip = """function (point) { return '<b>' + point.data.label + '</b>'; }"""
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





#Production des fichiers HTML de représentation en 3d dynamique des mesures avec coloration par cluster
def trace_artefact_3d(data, clusters, title="",label_col="",for_jupyter=False,pca_offset=0,w="800px",h="800px"):
    pca = decomp.pca.PCA(n_components=3+pca_offset)
    pca.fit(data)
    newdata = pca.transform(data)

    li_data = []
    for c in clusters:
        for k in range(len(c.index)):
            if label_col=="":
                label=""
            else:
                label=c.name+"<br>"+str(c.labels[k])

            li_data.append({
                'x': newdata[c.index[k], pca_offset],
                'y': newdata[c.index[k], pca_offset+1],
                'z': newdata[c.index[k], pca_offset+2],
                'style': c.position,
                'label':label,
                'cluster':c.name
            })

    code=""
    if len(title)>0:code="<h1>"+title+"</h1>"
    code=code+"<h3>Réprésentation 3d sur les axes "+str(pca_offset)+","+str(pca_offset+1)+","+str(pca_offset+2)+"</h3>"

    return code+draw_3D(li_data,for_jupyter=for_jupyter,lines=None,w=w,h=h)



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




