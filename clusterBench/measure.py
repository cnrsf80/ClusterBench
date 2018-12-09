import os
import werkzeug
from flask import request
from flask_restplus import Namespace, Resource, abort
import clusterBench.tools as tools
import pandas as pd
import base64

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
        subdir=request.remote_addr
        if request.args.get("public")=="true":subdir="public"
        url: str = tools.getPath(name, subdir)
        if "files" in request.files:
            file = request.files["files"]
            file.save(url)

            data = tools.get_data_from_url(name,subdir)

            data = tools.filter(data,request.args.get("filter", dict(), dict))

            if data is None:
                os.remove(url)
                return "Le fichier contient des valeurs incorrectes",422
            else:
                return "",201

        if request.data:
            with open(url,"w",encoding="utf-8") as text_file:
                if request.data:
                    b:bytes=request.data
                else:
                    b: bytes = request.form

                text_file.write(b.decode(encoding="utf-8",errors="ignore"))

            return "/job/"+name



    @api.doc(responses={201: 'The file exist'})
    @api.doc(params={'name':'Name of the file to check'})
    def get(self,name):
        decorators = []
        abort_if_file_doesnt_exist(name)

        url: str =tools.getPath(name,request.remote_addr)
        if name in os.listdir(url):
            return name+" exist",201
        else:
            return name + " not exist", 201



    @api.doc(params={'name': 'Name of the file to remove from server'})
    def delete(self,name):
        decorators = []
        abort_if_file_doesnt_exist(name)
        url = tools.getPath(name,request.remote_addr)
        os.remove(url)
        return '',204


#Retourne la liste des fichiers sur le serveur
@api.route("/measures")
class MeasureList(Resource):
    def get(self):
        s = os.listdir(tools.getPath("",request.remote_addr))+os.listdir(tools.getPath("","public"))
        return s,201
