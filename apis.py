from flask_restplus import Api

from clusterBench.measure import api as measure_ns
from clusterBench.jobs import api as jobs_ns
from clusterBench.job import ns_job
from clusterBench.graphics import ns_graphics

api=Api(
    contact="dev@f80.fr",
    version="1.0",
    title="3DataAPI",
    doc="/api",
    description="3D representation of cluster and graph"
)

api.add_namespace(measure_ns)
#api.add_namespace(jobs_ns)
api.add_namespace(ns_job)
api.add_namespace(ns_graphics)