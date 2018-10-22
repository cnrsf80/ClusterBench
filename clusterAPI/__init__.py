import os

from flask import Flask,request,g,render_template,redirect,url_for,jsonify
import clusterBench.simulation as simulation
import clusterBench.algo as algo
import pandas as pd
import main
import copy
import clusterBench.tools as tools
from sklearn import cluster as cl
import hdbscan
from simpledbf import Dbf5
import urllib

def gencode(data, params: str, name_algo: str):
    label_col = data.columns[0]
    dimensions = len(data.columns) - 1
    sim = simulation.simulation(data, label_col, dimensions)

    sim.raz()
    # if request.args["keep"] == None:

    # parameters={"min_elements": [1], "leaf_size": [10], "alpha": [1]}

    if name_algo.upper().__contains__("HDBSCAN"):
        parameters = tools.buildDict(params, {"min_samples": [3], "min_cluster_size": [2], "leaf_size": [20],
                                              "alpha": [0.5]})
        sim.execute(algo_name="HDBSCAN",
                    url="https://hdbscan.readthedocs.io/en/latest/how_hdbscan_works.html",
                    func=lambda x:
                    hdbscan.HDBSCAN(min_cluster_size=x["min_cluster_size"],
                                    leaf_size=x["leaf_size"],
                                    min_samples=x["min_samples"],
                                    alpha=x["alpha"]),
                    ps=parameters)

    if name_algo.upper().__contains__("MEANSHIFT"):
        parameters = tools.buildDict(params, {"bandwidth": [2]})
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
        parameters = tools.buildDict(params, {"passes": [10], "distance_toremove": [60]})
        for passes in parameters.get("passes"):
            for distance_toremove_edge in parameters.get("distance_toremove_edge"):
                m: algo.model = algo.create_cluster_from_neuralgasnetwork(
                    copy.deepcopy(sim.ref_model).clear_clusters(),
                    a=0.5,
                    passes=passes,
                    distance_toremove_edge=distance_toremove_edge)
                m.params = [passes, distance_toremove_edge, ""]
                m.help = "https://github.com/AdrienGuille/GrowingNeuralGas"
                sim.append_modeles(m)

    sim.init_metrics(False)

    code = sim.print_infos() + "<br>"

    try:
        n_pca = int(request.args["pca"])
    except:
        n_pca = 2

    code = code + sim.get3d_html(n_pca)

    if request.args.__contains__("notif") and len(request.args["notif"]) > 0:
        url_to_send = request.url.split("&notif")[0]

        url = ""
        url_to_send = url_to_send.replace(url, urllib.parse.quote_plus(url))

        body: str = "Traitement disponible <a href='" + url_to_send+"'>Ici</a>"

        tools.sendMail("ClusterBench : Fin de traitement", "cnrs.f80@gmail.com",
                       request.args["notif"],
                       body
                       )

    return code


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        #DATABASE=os.path.join(app.instance_path, 'clusterAPI.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    @app.route('/', methods=['GET'])
    def index():
        return render_template("index.html")

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ["xlsx","xls","csv","txt"]

    @app.route('/upload', methods=['POST'])
    def upload_file():
        # check if the post request has the file part
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join("./datas", filename))
            return jsonify(url=filename);


    @app.route('/files', methods=['GET'])
    def list_files():
        s=os.listdir(os.path.join("./datas",""))
        return '\n'.join(s)


    # url=http://f80.fr/cnrs/datas/PourClustering.csv
    # http://127.0.0.1:5000/datasfromurl/id/11/http%3A%2F%2Ff80.fr%2Fcnrs%2Fdatas%2FPourClustering.xlxs
    # http://127.0.0.1:5000/datasfromurl/id/11/http%3A%2F%2Ff80.fr%2Fcnrs%2Fdatas%2FPourClustering.xlxs


    #test : http://localhost:5000/algo/HDBSCAN/https%3A%2F%2Fmycore.core-cloud.net%2Findex.php%2Fs%2FUWSxBo17DQLDlU5%2Fdownload/min_cluster_size=3/modele.html?pca=2¬if=paul.dudule@gmail.com
    @app.route('/algo/<string:name_algo>/<path:url>/<string:params>/modele.html', methods=['GET'])
    def algo_func(url: str, params: str, name_algo: str):
        if not url.startswith("http:"):
            url=os.path.join("./datas", url)

        format=tools.AnalyseFile(url)
        data:pd.DataFrame = None
        try:
            if format=="excel": data = pd.read_excel(url)
            if format == "dbf": data = Dbf5(url).to_dataframe()
            if format == "csv" :
                data = pd.read_csv(url, sep=";",decimal=",")
                if not data is None and not type(data.iloc[3][3]) is float: data = pd.read_csv(url, sep=",", decimal=".")
                if not data is None and not type(data.iloc[3][3]) is float: data = pd.read_csv(url, sep=";", decimal=".")
        except:
            data = None

        if data is None: return "Erreur sur la source de donnée : " + url
        if not params.__contains__("="):return "erreur sur les parametres "+params

        return gencode(data,params,name_algo)



    @app.route('/datas/<string:label_col>/<int:dimensions>', methods=['POST'])
    def datas(label_col: str, dimensions: int):
        f = request.files[0]
        source_file: str = "./datas/" + f.name

        f.save(source_file)

        ref_mod: algo.model = simulation.create_reference_model(pd.read_excel(source_file), label_col, dimensions)
        g.sim = simulation.simulation(ref_mod, label_col, dimensions)

    @app.route('/trace')
    def trace():
        s: simulation.simulation = g.sim
        url = s.create_trace()
        return url

    # http://127.0.0.1:5000/exec/HDBSCAN
    @app.route('/exec/<string:algos>', methods=['GET'])
    def exec(algos: str):
        main.exec_algos(algos.upper(), g.sim)

    return app