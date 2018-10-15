from flask import Flask,request,g
import clusterBench.simulation as simulation
import clusterBench.algo as algo
import pandas as pd
import main


app = Flask(__name__)

# url=http://f80.fr/cnrs/datas/PourClustering.xlsx
# http://127.0.0.1:5000/datasfromurl/id/11/http%3A%2F%2Ff80.fr%2Fcnrs%2Fdatas%2FPourClustering.xlxs
# http://127.0.0.1:5000/datasfromurl/id/11/http%3A%2F%2Ff80.fr%2Fcnrs%2Fdatas%2FPourClustering.xlxs
@app.route('/datasfromurl/<label_col>/<int:dimensions>/<path:url>', methods=['GET'])
def datasfromurl(label_col:str,dimensions:int,url):
    #url="http://f80.fr/cnrs/datas/PourClustering.xlsx"
    data=pd.read_excel(url)
    s: simulation = simulation.simulation(data, label_col, dimensions)



@app.route('/datas/<string:label_col>/<int:dimensions>', methods=['POST'])
def datas(label_col:str,dimensions:int):
    f=request.files[0]
    source_file:str="./datas/"+f.name

    f.save(source_file)

    ref_mod:algo.model = simulation.create_reference_model(pd.read_excel(source_file), label_col,dimensions)
    g.sim=simulation.simulation(ref_mod, label_col, dimensions)


# http://127.0.0.1:5000/exec/HDBSCAN
@app.route('/exec/<string:algos>', methods=['GET'])
def exec(algos:str):
    main.exec_algos(algos.upper(),g.sim)


if __name__ == '__main__':
    app.run()
