from flask_restplus import Namespace, Resource
from flask import Response,Request
import pandas as pd
import clusterBench.tools as tools
import clusterBench.algo as algo
import clusterBench.draw as draw

ns_graph = Namespace('graph', description='Job related operations to calculation')

#test:http://localhost:5000/graph/karate.gml?algo_loc=modularity&algo_comm=gn
@ns_graph.route("/<string:url>")
class graph(Resource):
    def get(self,url:str):
        graph = None
        if url.endswith(".gml"):
            if not url.startswith("http"):url="./datas/"+url
            graph=algo.network(url=url)
        else:
            data:pd.DataFrame=tools.get_data_from_url(url)
            if not data is None:
                d=data.to_dict()
                graph=algo.network(data["ref"],d)

        if not graph is None:
            default_loc="spectral"
            if len(graph.graph.nodes)>10000:default_loc="circular"

            arguments = tools.add_default_value(Request.args.__dict__, {
                "algo_comm": "gn","algo_loc":default_loc
            })

            graph.node_treatments()
            graph.findClusters(method=arguments["algo_comm"])
            #graph.relocate(method=arguments["algo_loc"])
            graph.relocate(method="spectral")
            return Response(draw.trace_graph(graph),"text/html")




