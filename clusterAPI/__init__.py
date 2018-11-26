import os
from flask import Flask,request,g,render_template


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
        html="<select onmouseup='showlink()' id='lst_files'>"
        for s in os.listdir(os.path.join("./datas", "")):
            html=html+"<option>"+s+"</option>"

        return render_template("index.html",list_file=html+"</select>")

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