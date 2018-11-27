from flask_restplus import Namespace, Resource
from flask import Response,request
import clusterBench.tools as tools
import clusterBench.simulation as simulation
import time

ns_job = Namespace('job', description='Job related operations to calculation')

#test:http://localhost:5000/job/Armure_Resultats.xlsx/HDBSCAN/min_samples=2&min_cluster_size=3&alpha=0.5?pca=1
#test:http://localhost:5000/job/lycees.csv/HDBSCAN/min_samples=3&min_cluster_size=6&alpha=0.5&?pca=1&filter=1,2,8,9,10,11,20,21,22,23,60,61,62,90,91,92

@ns_job.route("/<string:url>/<string:algo>/<string:params>")
@ns_job.param("url","url address of the file to treat")
@ns_job.param("algo","name of the algo to run. Name must be in HDBSCAN,SPECTRAL,HAC,NEURALGAS")
@ns_job.param("params","parameters of the algorithm to run")
@ns_job.param("pca","Number of views")
class job(Resource):
    def get(self,url,algo,params):
        #arguments = tools.add_default_value(request.args,{"no_text": False,"no_metric": False,"pca":1,"notif":""})

        tmp_data=tools.get_data_from_url(url)
        data = tools.removeNan(tools.filter(tmp_data,request.args.get("filter","")))

        if len(data)==0:
            return "No data after filtering",501

        start = time.time()

        notext=(request.args.get("notext", "False",str)=="True")
        nometrics = (request.args.get("nometrics", "False",str)=="True")
        sim:simulation = simulation.simulation(data=data,no_metric=nometrics,format=request.args.get("format",""))

        sim.run_algo(params, algo)
        if not nometrics:
            sim.init_metrics(showProgress=False)

        html=sim.toHTML(request.args.get("autorotate","false",str),no_text=notext,no_metrics=nometrics)

        delay = (time.time() - start)

        if delay > 10 and len(request.args.get("notif","",str))> 0:
            # url_to_send = request.url.split("&notif")[0]
            url_to_send = url

            body: str = "Traitement disponible <a href='" + url_to_send + "'>Ici</a>"

            tools.sendMail("ClusterBench : Fin de traitement", "cnrs.f80@gmail.com",
                           request.args.get("notif", "", str),body
                           )

        return Response(html,mimetype="text/html")
