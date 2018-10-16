from flask import Flask,request,g
import clusterBench.simulation as simulation
import clusterBench.algo as algo
import pandas as pd
import main
import copy
import clusterBench.tools as tools
from sklearn import cluster as cl
import hdbscan

app = Flask(__name__)

# url=http://f80.fr/cnrs/datas/PourClustering.csv
# http://127.0.0.1:5000/datasfromurl/id/11/http%3A%2F%2Ff80.fr%2Fcnrs%2Fdatas%2FPourClustering.xlxs
# http://127.0.0.1:5000/datasfromurl/id/11/http%3A%2F%2Ff80.fr%2Fcnrs%2Fdatas%2FPourClustering.xlxs
@app.route('/datasfromurl/<label_col>/<int:dimensions>/<path:url>', methods=['GET'])
def datasfromurl(label_col:str,dimensions:int,url):
    #url="http://f80.fr/cnrs/datas/PourClustering.xlsx"
    data=pd.read_excel(url)
    s: simulation = simulation.simulation(data, label_col, dimensions)


@app.route('/', methods=['GET'])
def index():
    code="Exemple de commandes possible :<br>"
    code=code+tools.addlink("http://127.0.0.1:5000/algo/hdbscan/http%3A%2F%2Ff80.fr%2Fcnrs%2Fdatas%2FPourClustering.csv/min_cluster_size=3")
    code=code+tools.addlink("http://127.0.0.1:5000/algo/hac/http%3A%2F%2Ff80.fr%2Fcnrs%2Fdatas%2FPourClustering.csv/n_clusters=12,11,13")
    code=code+tools.addlink("http://127.0.0.1:5000/algo/meanshift/http%3A%2F%2Ff80.fr%2Fcnrs%2Fdatas%2FPourClustering.csv/bandwidth=0.1,0.3,0.2")
    code=code+tools.addlink("http://127.0.0.1:5000/algo/hdbscan/http%3A%2F%2Ff80.fr%2Fcnrs%2Fdatas%2FPourClustering.csv/min_cluster_size=5,6,7,8&alpha=0.1,0.3,0.5,0.9")
    code=code+tools.addlink("http://127.0.0.1:5000/algo/neuralgas/http%3A%2F%2Ff80.fr%2Fcnrs%2Fdatas%2FPourClustering.csv/passes=10,20,60,120&distance_toremove_edge=40")
    return code


@app.route('/algo/<string:name_algo>/<path:url>/<string:params>', methods=['GET'])
def algo_func(url:str,params:str,name_algo:str):
    data=None
    if url.endswith(".xlsx"):data=pd.read_excel(url)
    if url.endswith(".csv"):data=pd.read_csv(url,sep=";")
    if data is None:return "Erreur sur les data"

    label_col=data.columns[0]
    dimensions=len(data.columns)-1
    sim=simulation.simulation(data, label_col, dimensions)

    if request.form.get("keep")==None:
        sim.raz()

    #parameters={"min_elements": [1], "leaf_size": [10], "alpha": [1]}

    if name_algo.upper().__contains__("HDBSCAN"):
        parameters = tools.buildDict(params, {"min_cluster_size": [2], "leaf_size": [20], "alpha": [0.5]})
        sim.execute(algo_name="HDBSCAN",
                    url="https://hdbscan.readthedocs.io/en/latest/how_hdbscan_works.html",
                    func=lambda x:
                            hdbscan.HDBSCAN(min_cluster_size=x["min_cluster_size"], leaf_size=x["leaf_size"], alpha=x["alpha"]),
                    ps=parameters)

    if name_algo.upper().__contains__("MEANSHIFT"):
        parameters=tools.buildDict(params,{"bandwidth": [2]})
        sim.execute("MEANSHIFT",
                  "http://scikit-learn.org/stable/modules/generated/sklearn.cluster.MeanShift.html#sklearn.cluster.MeanShift",
                  lambda x:
                  cl.MeanShift(bandwidth=x["bandwidth"], bin_seeding=False, cluster_all=True),
                  parameters)

    if name_algo.upper().__contains__("HAC"):
        parameters = tools.buildDict(params, {"n_clusters": [12]})
        sim.execute("HAC",
                  "http://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html#sklearn.cluster.AgglomerativeClustering",
                  lambda x:
                    cl.AgglomerativeClustering(n_clusters=x["n_clusters"]),
                  parameters
                  )

    if name_algo.upper().__contains__("NEURALGAS"):
        parameters = tools.buildDict(params, {"passes": [50],"distance_toremove":[60]})
        for passes in parameters.get("passes"):
            for distance_toremove_edge in parameters.get("distance_toremove_edge"):
                m:algo.model = algo.create_cluster_from_neuralgasnetwork(
                    copy.deepcopy(sim.ref_model).clear_clusters(),
                    a=0.5,
                    passes=passes,
                    distance_toremove_edge=distance_toremove_edge)
                m.params = [passes, distance_toremove_edge, ""]
                m.help = "https://github.com/AdrienGuille/GrowingNeuralGas"
                sim.append_modeles(m)

    sim.init_metrics(False)

    code=sim.print_infos()+"<br>"+sim.get3d_html()
    return code


@app.route('/datas/<string:label_col>/<int:dimensions>', methods=['POST'])
def datas(label_col:str,dimensions:int):
    f=request.files[0]
    source_file:str="./datas/"+f.name

    f.save(source_file)

    ref_mod:algo.model = simulation.create_reference_model(pd.read_excel(source_file), label_col,dimensions)
    g.sim=simulation.simulation(ref_mod, label_col, dimensions)


# http://127.0.0.1:5000/exec/HDBSCAN
@app.route('/exec/<string:algos>', methods=['GET'])
def exec(algos:str):
    main.exec_algos(algos.upper(),g.sim)


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)
