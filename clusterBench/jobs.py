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
    # test : http://localhost:5000/engine/jobs?algoname=HDBSCAN&params=min_samples:2&min_cluster_size:3&alpha:0.5&url=Armure_Resultats.xlsx&pca=1
    # @api.route('/algo/<string:name_algo>/<path:url>/<string:params>/modele.html')
    @api.doc(params={"url": "file's address",
                     "params": "parameters list",
                     "algoname": "Algorithm name",
                     "notext": "Graphics only",
                     "nometric": "No metrics"
                     })

    @api.doc("Job's list")
    @api.param("")
    def get(self):
        s = os.listdir(os.path.join("./clustering", ""))
        return s, 201