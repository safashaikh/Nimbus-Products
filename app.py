from flask import Flask, Response, request, render_template, jsonify
from flask_cors import CORS

import database_services.RDBService as d_service
import json

import logging

import utils.rest_utils as rest_utils

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

from application_services.ProductResource.product_service import ProductResource



app = Flask(__name__)
CORS(app)


@app.route('/products', methods=["GET", "POST"])
def get_addresses():
    try:
        input = rest_utils.RESTContext(request)
        if input.method == "GET":
            res = ProductResource.get_by_template(None)
            rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")

        elif input.method == "POST":
            data = input.data
            res = ProductResource.add_by_template(data)
            rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")

        else:
            rsp = Response("Method not implemented", status=501)

    except Exception as e:
        print(f"Path: '/users', Error: {e}")
        rsp = Response("INTERNAL ERROR", status=500, content_type="text/plain")

    return rsp

@app.route('/products/<pid>', methods=["GET", "PUT", "DELETE"])
def get_address_by_pid(pid):
    try:
        input = rest_utils.RESTContext(request)
        if input.method == "GET":
            res = ProductResource.get_by_template({'pid': pid})
            rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")

        elif input.method == "PUT":
            data = input.data
            res = ProductResource.update_by_template(data, {'pid': pid})
            rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")

        elif input.method == "DELETE":
            res = ProductResource.delete_by_template({'pid': pid})
            rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")

        else:
            rsp = Response("Method not implemented", status=501)

    except Exception as e:
        print(f"Path: '/products/<pid>', Error: {e}")
        rsp = Response("INTERNAL ERROR", status=500, content_type="text/plain")

    return rsp


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)