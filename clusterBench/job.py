from flask_restplus import Namespace, Resource
from flask import Response,request,send_file
import clusterBench.tools as tools
import clusterBench.simulation as simulation
import time
import base64
import pandas as pd
import io

ns_job = Namespace('job', description='Job related operations to calculation')

#test:http://localhost:5000/job/Armure_Resultats.xlsx/HDBSCAN/min_samples=2&min_cluster_size=3&alpha=0.5?pca=1
#test:http://localhost:5000/job/lycees.csv/HDBSCAN/min_samples=3&min_cluster_size=6&alpha=0.5&?pca=1&filter=1,2,8,9,10,11,20,21,22,23,60,61,62,90,91,92

@ns_job.route("/<string:url>/<string:algo>/<string:params>")
@ns_job.param("url","url address of the file to treat")
@ns_job.param("algo","name of the algo to run. Name must be in HDBSCAN,SPECTRAL,HAC,NEURALGAS")
@ns_job.param("params","parameters of the algorithm to run")
@ns_job.param("pca","Number of views")
class job(Resource):
    def get(self,url:str,algo,params):
        if url.startswith("b64="):url=base64.standard_b64decode(url.split("b64=")[1]).decode("utf-8")

        tmp_data=tools.get_data_from_url(url,request.remote_addr)
        if tmp_data is None:tmp_data=tools.get_data_from_url(url,"public")

        format=request.args.get("format","")
        p_format:dict=tools.replace_index_by_name(tmp_data,format)
        data:pd.DataFrame = tools.removeNan(tools.filter(tmp_data,p_format))

        if len(data)==0:
            return "No data after filtering",501


        if request.args.get("limit",0,int)>0:data=data.iloc[list(range(0,min(len(data),request.args.get("limit",0,int))))]
        start = time.time()

        notext=(request.args.get("notext", "False",str)=="True")
        nometrics = (request.args.get("nometrics", "False",str)=="True")

        sim:simulation = simulation.simulation(data=data,no_metric=nometrics,format=p_format)

        sim.run_algo(params, algo)
        if not nometrics:
            sim.init_metrics(showProgress=False)

        if notext:
            html=""
        else:
            html = sim.print_infos() + "<br>synthese<br>"

        html = html + sim.get3d_html(request.args.get("pca",2,int),
                                     autorotate=(request.args.get("autorotate","True",str)=="True"),
                                     no_text=notext,
                                     add_property=request.args.get("property",False,bool))

        if nometrics:
            html = html.replace("synthese", "")
        else:
            html = html.replace("synthese", sim.synthese())


        delay = (time.time() - start)

        if delay > 10 and len(request.args.get("notif","",str))> 0:
            # url_to_send = request.url.split("&notif")[0]
            url_to_send = url

            body: str = "Traitement disponible <a href='" + url_to_send + "'>Ici</a>"

            tools.sendMail("ClusterBench : Fin de traitement", "cnrs.f80@gmail.com",
                           request.args.get("notif", "", str),body
                           )

        #Téléchargement du fichier excel
        if str(request.args.get("output", "")).startswith("csv"):
            return Response(response=sim.metrics.to_csv(index=False,sep=",",decimal="."),
                            mimetype="text/csv",
                            )

        if str(request.args.get("output", "")).startswith("csvfile"):
            output = io.BytesIO()
            output.write(sim.metrics.to_csv(index=False,sep=",",decimal="."))
            return send_file(output, mimetype="text/csv",
                             attachment_filename="synthese.csv", as_attachment=True)


        if str(request.args.get("output", "")).startswith("xls"):
            output = io.BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            sim.metrics.to_excel(excel_writer=writer)
            return send_file(output,
                             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             attachment_filename="synthese.xlsx",as_attachment=True)

        sim=None
        return Response(html,mimetype="text/html")

