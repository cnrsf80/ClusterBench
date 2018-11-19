from flask import request
from flask_restplus import Namespace, Resource
import clusterBench.tools as tools
import time,os
import clusterBench.simulation as simulation

api = Namespace('jobs', description='Jobs related operations to calculation')

@api.route("/jobs")
class jobs(Resource):

    # Api principale permetant l'execution des algorithmes de clustering
    # url : contient l'adresse internet de la source de données à traiter
    # test : http://localhost:5000/algo/HDBSCAN/https%3A%2F%2Fmycore.core-cloud.net%2Findex.php%2Fs%2FUWSxBo17DQLDlU5%2Fdownload/min_cluster_size=3/modele.html?pca=2¬if=paul.dudule@gmail.com
    # @api.route('/algo/<string:name_algo>/<path:url>/<string:params>/modele.html')
    @api.doc(params={"url": "file's address",
                     "params": "parameters list",
                     "algoname": "Algorithm name",
                     "notext": "Graphics only",
                     "nometric": "No metrics"
                     })
    def post(self):
        #Traitement des valeurs par défaut
        arguments=request.args.deepcopy()
        if not arguments.__contains__("algoname"):arguments.algoname="HDBSCAN"
        if not arguments.__contains__("params"):arguments.params="min_samples=2&min_cluster_size=3&alpha=1.0"
        if not arguments.__contains__("url"):arguments.url="Pour Clustering2.xls"

        algoname=arguments.algoname
        params=arguments.params
        url = arguments.url

        data = tools.get_data_from_url(url)

        if not params.__contains__("="): return "erreur sur les parametres " + params

        start = time.time()

        no_text = False
        if arguments.__contains__("notext"): no_text = True

        no_metric = False
        if arguments.__contains__("nometric"): no_metric = True

        sim:simulation=simulation(data=data)

        html = sim.run_algo(params, algoname,no_text, no_metric)
        delay = (time.time() - start)

        if delay > 10 and request.args.__contains__("notif") and len(request.args["notif"]) > 0:
            # url_to_send = request.url.split("&notif")[0]
            url_to_send = request.url
            # url = ""
            # url_to_send = url_to_send.replace(url, urllib.parse.quote_plus(url))

            body: str = "Traitement disponible <a href='" + url_to_send + "'>Ici</a>"

            tools.sendMail("ClusterBench : Fin de traitement", "cnrs.f80@gmail.com",
                           request.args["notif"],
                           body
                           )

        return html


    @api.doc("Job's list")
    @api.param("")
    def get(self):
        s = os.listdir(os.path.join("./clustering", ""))
        return s, 201