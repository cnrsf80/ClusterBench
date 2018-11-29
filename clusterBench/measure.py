import os

from flask import request
from flask_restplus import Namespace, Resource, abort
import clusterBench.tools as tools
import pandas as pd

api = Namespace('datas', description='Datas related operations to add / remove file on server')

def abort_if_file_doesnt_exist(name):
    url = os.path.join("./datas", name)
    if not os.path.isfile(url):
        abort(404, message=name+" doesn't exist")

#test:http://localhost:5000/measure/lycee?
#Représentation des fichiers à traiter
@api.route("/measure/<string:name>")
class Measure(Resource):
    # Retourne Vrai si le format du fichier est accepté
    def allowed_file(self,filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ["xlsx", "xls", "csv", "txt"]

    # Permet le chargement des fichiers sur le serveur
    @api.doc(responses={201: 'File created'})
    @api.doc(responses={401: 'Le fichier contient des valeurs incorrectes'})
    def post(self,name):
        if "files" in request.files:
            file = request.files["files"]
            url = os.path.join("./datas", name)
            file.save(url)
            data = tools.get_data_from_url(name)

            data = tools.filter(data,request.args.get("filter", "", str))

            if not tools.chk_integrity(data):
                os.remove(url)
                return "Le fichier contient des valeurs incorrectes",401
            else:
                return "",201

        if request.data:
            url = os.path.join("./datas", name)
            with open(url,"w",encoding="utf-8") as text_file:
                b:bytes=request.data
                text_file.write(b.decode(encoding="utf-8",errors="ignore"))
            return "/job/"+name


    @api.doc(responses={201: 'The file exist'})
    @api.doc(params={'name':'Name of the file to check'})
    def get(self,name):
        decorators = []
        abort_if_file_doesnt_exist(name)
        url = os.path.join("./datas", name)
        return name+" exist",201

    @api.doc(params={'name': 'Name of the file to remove from server'})
    def delete(self,name):
        decorators = []
        abort_if_file_doesnt_exist(name)
        url = os.path.join("./datas", name)
        os.remove(url)
        return '',204


#Retourne la liste des fichiers sur le serveur
@api.route("/measures")
class MeasureList(Resource):
    def get(self):
        s = os.listdir(os.path.join("./datas", ""))
        return s,201
