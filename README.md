#Installation
L'installation de l'API sur un serveur repose sur Docker.
 
Cette installation peut être réalisée simplement par la commande :
<pre>docker run --restart=always -v /clustering:/app/clustering -p 5000:5000 --name clusterbench -d f80hub/cluster_bench_x86:latest</pre>

La mise a jour du serveur peut se faire simplement par 
<pre>
docker rm -f clusterbench && docker pull f80hub/cluster_bench_x86:latest && docker run --restart=always -v /clustering:/app/clustering -p 5000:5000 --name clusterbench -d f80hub/cluster_bench_x86:latest
</pre>


#Utilisation de l'API via l'interface
Une interface permet un usage plus "user-friendly" de l'API. Elle est accessible à l'adresse du serveur sur le port 5000. 
L'utilisateur y sélectionne 
- l'algorithme de clustering à appliquer
- modifie les paramétres (qui dépendent de l'algorithme sélectionné)
- upload sur le serveur les données à traiter ou indique directement à l'API l'adresse internet ou trouver le fichier
- précise le nombre de vues pour la restitution graphique du clustering (voir complément sur la notion de vue)
- précise un email de notification de fin de traitement (voir complément sur la notification)

Au fil de l'eau des informations renseignées, un lien internet est fabriqué automatiquement. Ce lien peut
être ouvert pour lancer le traitement ou conserver pour un lancement ultérieur.

#Resultat du clustering
Le résultat du clustering se décompose en deux éléments :
    - un ensemble de métriques évaluant la pertinence du clustering en lui-même et vis a vis d'un clustering de référence
    - une ou plusieurs visualisation en 3 dimensions des mesures colorisées par cluster d'appartenance.

Si l'opération à consister à opérer plusieurs clustering, les résultats de chaque cluster sont précédé d'un tableau de synthèse
reprenant les différents paramétres appliqués à l'algorithme et les résultats en nombre de cluster obtenu et en métriques associées.

Le cluster de référence est donné dans le fichier des mesures soit
- par une colonne de libellé "Ref_cluster" contenant un code de regroupement pour chaque mesure (ligne du tableau)
- automatiquement, si la colonne ref_cluster n'existe pas, sur la base des mesures ayant le même libellé

#Visualisation
La visualisation dans l'espace nécessite un ordinateur récent surtout si le nombre de mesures est important. 
Cette fenêtre de visualisation offre de nombreuses possibilités d'analyse. 
L'ensemble des commandes est accessible par l'usage de la touche "h". Parmis ces possibilités ont peu lister :
- la possibilité de cacher certaines mesures ou au contraire de les rendres plus visible par grossissement
- de rechercher des mesures ou des clusters par nom 
- d'afficher des enveloppes autour des clusters
- de changer de point de vue pour visé une mesure / un cluster
- de supprimer le bruit (pour les algorithmes de clustering excluant certaines mesures comme HDBSCAN)
- d'enregistrer une vidéo
- d'exporter certaines données au format CSV (pour un éventuel retraitement)

La souris permet de se déplacer autour des clusters et de sélectionner les mesures


#Optimisation
L'ensemble des clustering sont conservés sur le serveur qui opére comme un cache avant d'effectuer les calculs.
Il est également possible de lancer plusieurs clustering en parallèle en précisant le nombre de process maximum à éxécuter.
Ce nombre dépend de la mémoire disponible sur le serveur. Le résultat des calculs parallèle est enregistrer dans le cache.

#Compléments
1/ Les vues
Graphiquement il est possible d'analyser les données sur plusieurs composantes des mesures à traiter. En général, on se
contente des 3 premières composantes qui portent souvent l'essentiel de l'information mais l'API donne le moyen de représenter
les autres composantes (PCA=nombre de vue)

2/ La notification
Une notification de fin de traitement est envoyé si :
 - un email à été précisé au lancement du traitement (paramètre notif du lien de lancement)
 - le temps de traitement excède 10 secondes
 
#Complément sur le code
Le code de l'API repose sur plusieurs framework :
 - "Flask", permet d'exposer le programme sous forme d'API
 - "Babylon.js" permet la representation 3D du clustering
 - "Scikit-learn" contient certains algorithmes de clustering et les calculs de métriques
 
D'autres librairies complémentaires sont incluse notamment :
 - "gng" contient une version adaptée pour python 3.6 de l'algotithme du gaz neuronal
 - "hdbscan" contient l'algorithme DBSCAN en version modifiée pour gérer les densités multiples
 
Le code est principalement contenu dans le répertoire clusterBench. 
Il repose sur 3 classes :
 - "cluster" : représentant un cluster, l'ensemble des points et des propriétés générales
 - "algo" : contient les paramétres d'un modèle, et la liste des clusters obtenus
 - "simulation" : contient une liste de modeles arpès éxécution et les métriques résultantes
 
Sur le serveur, les répertoires suivant contiennent :
- "metrics", une synthese du clustering
- "clustering", un cache du résultat de chaque calcul
 
 

 
#Exemples de requetes
- http://localhost:5000/job/lycees.csv/HDBSCAN/min_samples=5&min_cluster_size=6&alpha=0.5?&pca=0&format=cols:1,1,8,9,10,21,22,23,84,85,86,87,88,89,90,91_name:1
