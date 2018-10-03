import numpy as np
import random
import shutil
import os
import sys

#Permet l'affichage d'un barre de progression
def progress(count, total, suffix=''):
    bar_len = 50
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()  # As suggested by Rom Ruben


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
    shutil.rmtree("./"+name)
    os.mkdir("./"+name)