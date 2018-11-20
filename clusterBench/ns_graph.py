from flask_restplus import Namespace, Resource
from flask import Response
import os
import pandas as pd
import clusterBench.tools as tools
import clusterBench.algo as algo
import clusterBench.draw as draw

ns_graph = Namespace('graph', description='Job related operations to calculation')

#test:http://localhost:5000/graph/lesmis.gml
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
            graph.findClusters()
            pos=graph.relocate(3)
            return Response(draw.trace_graph(graph,pos),"text/html")




