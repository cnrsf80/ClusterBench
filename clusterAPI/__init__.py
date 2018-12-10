import os
from flask import Flask,request,g,render_template,jsonify
import clusterBench.tools as tools
import clusterBench.network as network
import clusterBench.algo as algo
import pandas as pd
import base64
import sklearn.cluster as cl


#http://45.77.160.220:5000/algo/NEURALGAS/Pour%20clustering2%20(1).xlsx/passes=30&distance_toremove_edge=50/modele.html?pca=2&notif=hhoareau%40gmail.com
#Créer une instance du serveur
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='cnrs',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    #Retourne la page d'acceuil du serveur d'API
    @app.route('/', methods=['GET'])
    def index():
        # html="<select onmouseup='showlink()' id='lst_files'>"
        # for s in os.listdir(os.path.join("./datas", "")):
        #     if not s.startswith("temp"):
        #         html=html+"<option>"+s+"</option>"

        return render_template("index.html")

    #test: http://localhost:5000/tograph/Armure_Resultats.xlsx?distance=0.2
    @app.route('/tograph/<string:name>', methods=['GET'])
    def export_as_graph(name:str):
        data,p_format = tools.get_data_from(name, request)
        G:network=network.network(data)
        if request.args.get("distance",0,float)>0:
            G.initByDistance(request.args.get("distance",0,float))
        else:
            G.execute("HAC", "", lambda x:cl.AgglomerativeClustering(request.args.get("n_clusters")))
            G.initByCluster()

        url=name.split(".")[0]+".gml"
        G.savegml(url)
        return url


    @app.route('/analyse/<string:url>', methods=['GET'])
    def analyse(url:str):
        type="data"
        data,p_format=tools.get_data_from(url,request)

        if not data is None and len(data)==0:
            G=None
            try:
                #todo: a améliorer la gestion du getpath
                G=network.network(url,request.remote_addr)
                result: pd.DataFrame = G.print_properties()
            except:
                pass
            if G is None:
                return "Unknown format"
            else:
                type="graph"
        else:
            result:pd.DataFrame=tools.analyse_data(data,request.args.get("filter",""))

        if request.args.get("format")=="json":
            d:dict={"columns":result.to_dict(orient="records"),"rows":len(data),"type":type}
            return jsonify(d)
        else:
            return result.to_html()


    @app.route('/show/<string:url>', methods=['GET'])
    def showFile(url:str):
        url=base64.standard_b64decode(url).decode("utf-8")
        return url



    @app.route('/log', methods=['GET'])
    def getlog():
        s=""
        with open("log.txt", "r") as log_file:
            s=s+log_file.read()

        return s.replace("\n","<br>")

    # @app.route('/datas/<string:label_col>/<int:dimensions>', methods=['POST'])
    # def datas(label_col: str, dimensions: int):
    #     f = request.files[0]
    #     source_file: str = "./datas/" + f.name
    #     f.save(source_file)
    #     ref_mod: algo.model = simulation.create_reference_model(pd.read_excel(source_file), label_col, dimensions)
    #     g.sim = simulation.simulation(ref_mod, label_col, dimensions)
    #
    #
    #
    # @app.route('/trace')
    # def trace():
    #     s: simulation.simulation = g.sim
    #     url = s.create_trace()
    #     return url
    #
    # # http://127.0.0.1:5000/exec/HDBSCAN
    # @app.route('/exec/<string:algos>', methods=['GET'])
    # def exec(algos: str):
    #     main.exec_algos(algos.upper(), g.sim)

    return app