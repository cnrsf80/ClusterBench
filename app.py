import clusterAPI
from apis import api
from flask_cors import CORS

if __name__ == '__main__':
    app=clusterAPI.create_app()
    CORS(app,resources={r"/datas/*": {"origins": "*"}})
    api.init_app(app)

    app.run(host="0.0.0.0",port=5000,debug=False,ssl_context="adhoc")
