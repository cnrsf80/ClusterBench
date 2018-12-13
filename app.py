import clusterAPI
from apis import api
from flask_cors import CORS

import ssl

if __name__ == '__main__':
    app=clusterAPI.create_app()
    CORS(app)
    api.init_app(app)

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain("fullchain.pem", "privkey.pem")

    #app.run(host="0.0.0.0",port=5000,debug=True)
    app.run(host="0.0.0.0",port=5000,debug=False,ssl_context=context)