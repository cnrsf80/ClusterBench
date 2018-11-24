from flask_restplus import Namespace, Resource
from flask import Response,request
import clusterBench.tools as tools
import clusterBench.simulation as simulation
import time

ns_job = Namespace('job', description='Job related operations to calculation')

#test:http://localhost:5000/engine/job/Armure_Resultats.xlsx/HDBSCAN/min_samples=2&min_cluster_size=3&alpha=0.5&?pca=1
@ns_job.route("/<string:url>/<string:algo>/<string:params>")
@ns_job.param("url","url address of the file to treat")
@ns_job.param("algo","name of the algo to run. Name must be in HDBSCAN,SPECTRAL,HAC,NEURALGAS")
@ns_job.param("params","parameters of the algorithm to run")
@ns_job.param("pca","Number of views")
class job(Resource):
    def get(self,url,algo,params):
        #arguments = tools.add_default_value(request.args,{"no_text": False,"no_metric": False,"pca":1,"notif":""})

        data = tools.get_data_from_url(url)

        if not params.__contains__("="):
            return "erreur sur les parametres " + params

        start = time.time()


        sim: simulation = simulation.simulation(data=data)

        sim.run_algo(params, algo)
        if not request.args.get("no_metric",False,bool):sim.init_metrics(False)
        html=sim.toHTML(request.args.get("autorotate","false",str))

        delay = (time.time() - start)

        if delay > 10 and len(request.args.get("notif","",str))> 0:
            # url_to_send = request.url.split("&notif")[0]
            url_to_send = url

            body: str = "Traitement disponible <a href='" + url_to_send + "'>Ici</a>"

            tools.sendMail("ClusterBench : Fin de traitement", "cnrs.f80@gmail.com",
                           request.args.get("notif", "", str),body
                           )

        return Response(html,mimetype="text/html")
