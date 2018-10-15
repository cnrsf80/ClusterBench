from flask import Flask,request,g
import clusterBench.simulation as simulation
import clusterBench.algo as algo
import pandas as pd
import main
import clusterBench.tools as tools
from sklearn import cluster as cl
import hdbscan

app = Flask(__name__)

# url=http://f80.fr/cnrs/datas/PourClustering.xlsx
# http://127.0.0.1:5000/datasfromurl/id/11/http%3A%2F%2Ff80.fr%2Fcnrs%2Fdatas%2FPourClustering.xlxs
# http://127.0.0.1:5000/datasfromurl/id/11/http%3A%2F%2Ff80.fr%2Fcnrs%2Fdatas%2FPourClustering.xlxs
@app.route('/datasfromurl/<label_col>/<int:dimensions>/<path:url>', methods=['GET'])
def datasfromurl(label_col:str,dimensions:int,url):
    #url="http://f80.fr/cnrs/datas/PourClustering.xlsx"
    data=pd.read_excel(url)
    s: simulation = simulation.simulation(data, label_col, dimensions)


@app.route('/', methods=['GET'])
def index():
    code="Exemple de commandes :<br>"
    code=code+"http://127.0.0.1:5000/algo/hdbscan/http%3A%2F%2Ff80.fr%2Fcnrs%2Fdatas%2FPourClustering.csv/min_samples=3<br>"
    code=code+"http://127.0.0.1:5000/algo/hac/http%3A%2F%2Ff80.fr%2Fcnrs%2Fdatas%2FPourClustering.csv/n_clusters=12<br>"
    code=code+"http://127.0.0.1:5000/algo/meanshift/http%3A%2F%2Ff80.fr%2Fcnrs%2Fdatas%2FPourClustering.csv/bandwidth=5<br>"
    return code


@app.route('/algo/<string:name_algo>/<path:url>/<string:params>', methods=['GET'])
def algo(url:str,params:str,name_algo:str):
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
        parameters = tools.buildDict(params, {"min_samples": [1], "leaf_size": [20], "alpha": [0.5]})
        sim.execute(algo_name="HDBSCAN",
                    url="https://hdbscan.readthedocs.io/en/latest/how_hdbscan_works.html",
                    func=lambda x:
                            hdbscan.HDBSCAN(min_samples=x["min_samples"], leaf_size=x["leaf_size"], alpha=x["alpha"]),
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
    app.run()
