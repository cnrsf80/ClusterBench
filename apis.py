from flask_restplus import Api

from clusterBench.measure import api as measure_ns
from clusterBench.job import ns_job
from clusterBench.graphics import ns_graphics
from clusterBench.ns_graph import ns_graph

api=Api(
    contact="dev@f80.fr",
    version="1.0",
    title="3DataAPI",
    doc="/api",
    description="An interactive 3D representation of clusters and graphs"
)

api.add_namespace(measure_ns)
api.add_namespace(ns_job)
api.add_namespace(ns_graphics)
api.add_namespace(ns_graph)