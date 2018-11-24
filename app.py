import clusterAPI
from apis import api

if __name__ == '__main__':
    app=clusterAPI.create_app()
    api.init_app(app)
    app.run(host="0.0.0.0",port=5000,debug=False)
