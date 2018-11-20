from flask_restplus import Namespace, Resource
from flask import Response,Request
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
        arguments = tools.add_default_value(Request.args.__dict__,
                                            {"no_text": False,"no_metric": False,"pca":1,"notif":""}
                                            )

        data = tools.get_data_from_url(url)

        if not params.__contains__("="):
            return "erreur sur les parametres " + params

        start = time.time()


        sim: simulation = simulation.simulation(data=data)

        html = sim.run_algo(params, algo, arguments["no_text"], arguments["no_metric"])
        delay = (time.time() - start)

        if delay > 10 and len(arguments["notif"])> 0:
            # url_to_send = request.url.split("&notif")[0]
            url_to_send = url

            body: str = "Traitement disponible <a href='" + url_to_send + "'>Ici</a>"

            tools.sendMail("ClusterBench : Fin de traitement", "cnrs.f80@gmail.com",
                           arguments.notif,
                           body
                           )

        return Response(html,mimetype="text/html")
