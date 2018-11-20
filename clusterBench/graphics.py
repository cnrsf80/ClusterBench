from flask_restplus import Namespace, Resource
from flask import Response,Request
import clusterBench.tools as tools
import clusterBench.simulation as simulation
import clusterBench.draw as draw

ns_graphics = Namespace('graphics', description='Job related operations to calculation')

#test:http://localhost:5000/engine/job/Armure_Resultats.xlsx/HDBSCAN/min_samples=2&min_cluster_size=3&alpha=0.5&?pca=1
@ns_graphics .route("/<string:url>/<string:algo>/<string:params>")
@ns_graphics .param("url","url address of the file to treat")
@ns_graphics .param("algo","name of the algo to run. Name must be in HDBSCAN,SPECTRAL,HAC,NEURALGAS")
@ns_graphics .param("params","parameters of the algorithm to run")
@ns_graphics .param("pca","Number of views")
class graphics(Resource):
    def get(self,url,algo,params):
        data = tools.get_data_from_url(url)
        sim: simulation = simulation.simulation(data=data,no_metric=True)
        sim.run_algo(params,algo)
        html=draw.trace_artefact_GL(sim.models[0])
        return Response(html,"text/html")