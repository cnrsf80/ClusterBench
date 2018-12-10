import numpy as np
import random
import shutil
import base64
import os
import sys
import pandas
from sklearn import preprocessing
import zipfile
import io
from flask import request


#Permet l'affichage d'un barre de progression
def progress(count, total, suffix=''):
    bar_len = 50
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s                                          \r' % (bar, percents, '%', suffix))
    sys.stdout.flush()  # As suggested by Rom Ruben
    with open("log.txt", "a") as log_file:
        log_file.write('[%s] %s%s ...%s                                          \r' % (bar, percents, '%', suffix))


#fabrique un fichier HTML sur la base du code
def create_html(name="index.html",code="",url_base=""):
    file=open("./saved/"+name+".html","w")
    code=code.replace("\n","<br>")
    file.write(code)
    file.close()
    if len(url_base)>0:
        return url_base+"/"+name+".html"
    else:
        return ""

#Permet la fabrication d'une matrice de distance
def create_matrix(data,seuil):
    if os.path.isfile("adjacence_artefact.csv") and len(data)>149:
        matrice=np.asmatrix(np.loadtxt("adjacence_artefact.csv",delimiter=" "))
    else:
        matrice = np.asmatrix(np.zeros((len(data),len(data))))

        np.savetxt("adjacence_artefact.csv",matrice)

    if(seuil==0):
        matrice_ww=matrice
    else:
        v_seuil = np.vectorize(lambda x, y: 1 if x < y else 0)
        matrice_ww=v_seuil(matrice,seuil)

    return matrice_ww

#tirage aléatoire d'une chaine de caractère
def tirage(str):
    return random.choice(str)

#effacement d'un répertoire
def clear_dir(name):
    try:
        shutil.rmtree("./"+name)
        os.mkdir("./"+name)
        return True
    except:
        return False


def save(df,filename,_print=False):
    if _print:print("Enregistrement dans "+filename)
    code=""
    if type(df) is str:code=df

    if type(df) is pandas.DataFrame:
        if str(filename).endswith(".xlsx"):
            writer = pandas.ExcelWriter(filename)
            df.to_excel(writer, "Sheet1")
            writer.save()

        if str(filename).endswith("html"):
            code=df.to_csv()

        if str(filename).endswith("html"):
            code=df.to_html()

    if len(code)>0:
        file = open(filename, "w")
        file.write(code)
        file.close()

    return filename


def mkdir(dir_name):
    if not os.listdir(".").__contains__(dir_name):
        os.mkdir(dir_name)
        return True
    else:
        return False

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def convert_to_number(v):
    if not is_number(v):
        return v
    else:
        if v.__contains__("."):
            return float(v)
        else:
            return int(v)

#Construit un dictionnaire a partir de la syntaxe param1=value1,param2=value2
def buildDict(params:str,rc=dict()):
    for s in params.split("&"):
        if len(s)>0 and s.index("=")>-1:
            k=s.split("=")[0]
            v=s.split("=")[1]
            if not type(v) is list:
                if v.__contains__(","):
                    tmp=[]
                    for vv in v.split(","):
                        tmp.append(convert_to_number(vv))
                    v=tmp
                else:
                    if is_number(v) and type(v) is str:
                        v=[convert_to_number(v)]
                    else:
                        v=[v]
            rc[k]=v

    return rc

def addlink(url,libele="",target="_blank"):
    if libele=="":libele=url
    return "<a target="+target+" href='"+url+"'>"+libele+"</a><br>"


def normalize(path:str):
    return path.replace(" ","_")

import smtplib
import email.mime.multipart as multipart
import email.mime.text as mimetext

def sendMail(subject:str,_from:str,to:str,body:str):
    if to is None:to="rv@f80.fr"
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    msg=multipart.MIMEMultipart()
    msg["From"]=_from
    msg["To"]=to
    msg["Subject"]=subject
    msg.attach(mimetext.MIMEText(body,"html"))

    try:
        server.login(_from, "hh4271!!")
        server.sendmail(_from,to, msg.as_string())
        server.quit()
    except:
        print("Email non envoyé")


import urllib.request
def AnalyseFile(url:str):
    if url.endswith(".gexf") or url.endswith(".gml"): return "graph"
    if url.endswith(".xlsx") or url.endswith(".xls"): return "excel"
    if url.endswith(".csv") or "format=csv" in url: return "csv"
    with urllib.request.urlopen(url) as response:
        data: str = response.read()
        if data.__contains__("rels/workbook"):return "excel"
        return "csv"
    return None

#Assure l'importation des données depuis une url en acceptant plusieurs format ==> conversion en dataframe
import pandas as pd
from simpledbf import Dbf5
def get_data_from_url(url:str,remote_addr:str):
    if not url.startswith("http"):
        url = getPath(url,remote_addr)

    format = AnalyseFile(url)
    if format=="graph":
        return pd.DataFrame() #On retourne un dataframe vide mais pas None

    data: pd.DataFrame = None
    try:
        if format == "excel": data = pd.read_excel(url)
        if format == "dbf": data = Dbf5(url).to_dataframe()
        if format == "csv":
            try:
                data = pd.read_csv(url, sep=";", decimal=".")
            except:
                pass

            try:
                if data is None or len(data.columns)<3:data = pd.read_csv(url, sep=";", decimal=",")
            except:
                pass

            try:
                if data is None or len(data.columns) < 3: data = pd.read_csv(url, sep=",", decimal=".")
            except:
                pass

    except OSError as err:
        print("RuntimeError ".format(err))
        data = None

    if data is None:
        print("Erreur sur la source de donnée : " + url)

    return data


def get_data_from(url:str,request):
    data=get_data_from_url(url,request.remote_addr)
    if data is None:data=get_data_from_url(url,"public")
    p_format=""
    if not data is None:
        format = request.args.get("filter", "")
        p_format: dict = replace_index_by_name(data, format)
        data= removeNan(filter(data, p_format))

    return data,p_format

#Permet de vérifier que l'ensemble des mesures n'est pas null
import math
def chk_integrity(data:pd.DataFrame):
    for row in data.values:
        for cel in row:
            if not type(cel) is str:
                if not is_number(cel):return False

    return True

import tokenize as tk
def tokenize(items:list):
    rc=[]
    s=set(items)
    ref_items=dict(zip(list(s),range(len(s))))
    for item in items:
        rc.append(ref_items[item])

    return rc


def add_default_value(args_from_url:dict, param):
    for p in param:
        if not p in args_from_url:
            args_from_url[p]=param[p]

    return args_from_url


def filter(data:pd.DataFrame,filter:dict):
    if len(filter.keys())==0:
        return data

    tmp = pd.DataFrame()
    for k in filter.keys():
        tmp[filter[k]] = data[filter[k]]

    return tmp


#Supprime les lignes ayant une valeur vide
def removeNan(data:pd.DataFrame):
    if data is None:return data

    n_rows=len(data)
    rc=data.dropna()
    print("row remove : "+str(n_rows-len(rc)))
    return rc

#Opere une réduction-centralisation des données
def normalize(data:pd.DataFrame):
    min_max_scaler = preprocessing.MinMaxScaler()
    np_scaled = min_max_scaler.fit_transform(data)
    return pd.DataFrame(np_scaled)

#Produit une analyse qualitative des données : % de données manquantes
def analyse_data(data:pd.DataFrame,format=""):
    data=filter(data,string_to_dict(format,":","_"))

    rc:pd.DataFrame=pd.DataFrame(
        {
            'Names':list(data.columns.values),
            'Empty(%)':list(round(100*data.isna().sum()/len(data))),
            'Complexity(%)':[100] * len(data.columns),
            'dataType':["float"] * len(data.columns),
            'Type':["measure"] * len(data.columns)
        }
        ,index=list(range(0,len(data.columns))))

    findIndex=False
    for i in range(len(rc)):
        progress(i, len(rc), "Propriétés de " + data.columns[i])
        if rc["Empty(%)"][i]>50:
            rc.at[i,"Type"]="exclude"
        else:
            if not findIndex:
                rc.at[i,"Type"]="index"
                findIndex=True

        if data[rc["Names"][i]].dtype == object:
            rc.at[i,"dataType"]="string"
            rc.at[i,"Complexity(%)"] = getComplexity(data[data.columns[i]])


    return rc


def getComplexity(l:list):
    return round(100*(len(set(l)) / len(l)))

def string_to_dict(format:str,equal_operator="=",sep="&"):
    rc=dict()
    for rel in format.split(sep):
        if equal_operator in rel:
            rc[rel.split(equal_operator)[0]]=rel.split(equal_operator)[1]

    return rc


def replace_index_by_name(tmp_data:pd.DataFrame, format:str):
    rc=dict()
    p:dict=string_to_dict(format,":","_")
    for key in p.keys():
        l=[]
        for col in p[key].split(","):
            if len(col)>0:l.append(tmp_data.columns[int(col)])
        rc[key]=l

    return rc


def getUrlForFile(name:str,remote_addr:str):
    if name.startswith("http"):return name

    url=getPath("",remote_addr)
    if name in os.listdir(url):
        return getPath(name,remote_addr)
    else:
        return getPath(name, "public")

def getPath(name, remote_addr):
    if name.startswith("http"):return name
    subdir=str(base64.b64encode(str.encode(remote_addr)),"UTF-8")
    if not subdir in os.listdir("./datas"):os.mkdir("./datas/"+subdir)
    if len(name)>0:
        return os.path.join("./datas/" + subdir + "/", name)
    else:
        return os.path.join("./datas/" + subdir,"")


import requests
def dezip(url:str):
    url=url.strip()
    if url.endswith(".zip") or url.endswith(".gz") or url.endswith(".tar"):
        name=str(base64.b64encode(str.encode(url)),"UTF-8")
        path=getPath(name,"zip")
        with zipfile.ZipFile(io.BytesIO(requests.get(url).content)) as zip_ref:
            zip_ref.extractall(path)

        files=os.listdir(path)
        return path+"/"+files[0]

        return path
    else:
        return url


