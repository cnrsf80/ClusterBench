<h1>Pre-requis</h1>
Une distribution, idéalement Linux et Python 3.6 installé
l'utilitaire "pip3" également installé (https://pip.pypa.io/en/latest/installing/)


<h1>Première Installation</h1>
Cloner le dépôt :<br> 
git clone https://github.com/cnrsf80/ClusterBench

Installer les librairies python nécéssaire au fonctionnement<br> 
pip3 install -r ClusterBench/requirements.txt

<h1>Mise a jour</h1>
ou si déjà cloner, le mettre a jour :<br>

cd ClusterBench
git pull origin master 

#Execution 
Ouvrir main.ipynb dans le notebook jupyter
ou en ligne de commande executer :
python3 main.py

#Resultats
Les répertoires suivant contiennent :
 - "metrics", une synthese du clustering
 - "saved", l'ensemble des représentations 2D et 3D des modeles
 - "clustering", un cache du résultat de chaque calcul

#Code
Le code est principalement contenu dans le répertoire clusterBench. Il repose sur 3 classes :
 - "cluster" : contient le détail d'un cluster
 - "algo" : contient les paramétres d'un modele, et les clusters obtenus
 - "simulation" : contient une liste de modeles arpès éxécution 

# Installation d'un Serveur Jupyter Notebook
Installation depuis :
    https://github.com/movalex/rpi-jupyter-conda
    
Accès 
    http://f80.fr:8888