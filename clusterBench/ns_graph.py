from flask_restplus import Namespace, Resource
from flask import Response,request
import clusterBench.tools as tools
import clusterBench.algo as algo
import clusterBench.draw as draw
import base64
import clusterBench.network as network

ns_graph = Namespace('graph', description='Graph module')

#test:http://localhost:5000/graph/netscience.gml/fr?algo_comm=asyncfluid
@ns_graph.route("/<string:url>/<string:algo_loc>")
@ns_graph.param("algo_comm","Clustering algorithm : lab,mod,async")
@ns_graph.param("number_of_comm","Community number for async_fluid algorithm")
@ns_graph.param("threshold","threshold to use to transform an distance matrix to graph")
@ns_graph.param("autorotate","Autostart the rotation of the graphique")
class graph(Resource):
    def get(self,url:str,algo_loc:str):
        if url.startswith("b64="): url = base64.standard_b64decode(url.split("b64=")[1]).decode("utf-8")
        graph = network.network(url=url,remote_addr=request.remote_addr,algo_loc=algo_loc)
        if not graph is None:
            if request.args.get("metrics", "true", str)=="true":graph.node_treatments()

            graph.findClusters(
                method=request.args.get("algo_comm","",str),
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




