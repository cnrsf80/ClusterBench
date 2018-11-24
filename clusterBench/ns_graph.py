from flask_restplus import Namespace, Resource
from flask import Response,request
import clusterBench.tools as tools
import clusterBench.algo as algo
import clusterBench.draw as draw

ns_graph = Namespace('graph', description='Job related operations to calculation')

#test:http://localhost:5000/graph/netscience.gml/fr?algo_comm=asyncfluid
@ns_graph.route("/<string:url>/<string:algo_loc>")
@ns_graph.param("algo_comm","Clustering algorithm : lab,mod,async")
@ns_graph.param("number_of_comm","Community number for async_fluid algorithm")
@ns_graph.param("seuil","seuil to use to transform an distance matrix to graph")
@ns_graph.param("autorotate","Autostart the rotation of the graphique")
class graph(Resource):
    def get(self,url:str,algo_loc:str):
        graph = algo.network(url=url,algo_loc=algo_loc)
        if not graph is None:

            graph.node_treatments()
            graph.findClusters(
                method=request.args.get("algo_comm","gn",str),
                number_of_comm=request.args.get("number_of_community",5,int)
            )

            pos=graph.relocate(
                method=request.args.get("algo_loc","fr",str)
                )

            html=Response(
                draw.trace_graph(graph,pos,request.args.get("autorotate","false",str)),
                "text/html"
            )

            graph.save()

            return html




