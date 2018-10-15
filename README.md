<h1>Pre-requis</h1>
Une distribution, idéalement Linux et Python 3.6 installé
Git installé pour récupérer le code (https://gist.github.com/derhuerst/1b15ff4652a867391f03)
l'utilitaire "pip3" également installé (https://pip.pypa.io/en/latest/installing/)

<h1>Première Installation</h1>
Cloner le dépôt :<br> 
git clone https://github.com/cnrsf80/ClusterBench

Installer les librairies python nécéssaire au fonctionnement<br> 
pip3.7 install -r ./ClusterBench/requirements.txt

<h1>Mise a jour</h1>
ou si déjà cloner, le mettre a jour :<br>

cd ClusterBench<br>
git pull origin master 

<h1>Execution</h1> 
Ouvrir main.ipynb dans le notebook jupyter<br>
ou en ligne de commande executer :<br>
cd ClusterBench<br>
python3 main.py<br>

ou bien lancer le serveur 

<h1>Resultats</h1>
Les répertoires suivant contiennent :
 - "metrics", une synthese du clustering
 - "saved", l'ensemble des représentations 2D et 3D des modeles
 - "clustering", un cache du résultat de chaque calcul

<h1>Code</h1>
Le code est principalement contenu dans le répertoire clusterBench. Il repose sur 3 classes :
 - "cluster" : contient le détail d'un cluster
 - "algo" : contient les paramétres d'un modele, et les clusters obtenus
 - "simulation" : contient une liste de modeles arpès éxécution 

<h1>Infrastructure</h1>
Installation depuis :
    https://github.com/movalex/rpi-jupyter-conda
    
Accès 
    http://f80.fr:8888
    
<h2>Server de calcul</h2>
Installation d'un serveur Fedora serveur<br>
puis installation de cuda :
 - dnf install http://developer.download.nvidia.com/compute/cuda/repos/fedora27/x86_64/cuda-repo-fedora27-9.2.148-1.x86_64.rpm<br>
 - dnf clean all`<br>
 - dnf install cuda<br>
<br>Puis installation de pyCUDA :
 - wget https://files.pythonhosted.org/packages/58/33/cced4891eddd1a3ac561ff99081019fddc7838a07cace272c941e3c2f915/pycuda-2018.1.1.tar.gz
 - tar xfz pycuda-2018.1.1.tar.gz<br>
 - cd pycuda-VERSION<br>
 - su -c "python distribute_setup.py" # this will install distribute
 - su -c "easy_install numpy" # this will install numpy using distribute
 <br>puis test :
  - cd pycuda-VERSION/test
  - python test_driver.py
 
 puis installation de PyCUDA:
  - tar xfz pycuda-VERSION.tar.gz`
    
#Fabrication de l'image docker
build : docker build -t hhoareau/cluster_bench_server . 
deploiement : docker push hhoareau/cluster_bench_server:latest
