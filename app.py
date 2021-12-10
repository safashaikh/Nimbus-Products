import json
import logging

from datetime import datetime

from flask import Flask, Response
from flask import request, render_template, jsonify
from flask_cors import CORS

from middleware.service_helper import _get_service_by_name, _generate_product_links, _generate_pages

import utils.rest_utils as rest_utils

from pprint import pprint

app = Flask(__name__)
CORS(app)


@app.route('/products', methods=["GET", "POST"])
def get_products():
    try:
        inputs = rest_utils.RESTContext(request)
        service = _get_service_by_name("product_service")
        if service is not None:
            if inputs.method == 'GET':
                res, total_count = service.find_by_template(inputs.args, inputs.fields, inputs.limit, inputs.offset)
                if res is not None:
                    res = _generate_product_links(res)
                    res = _generate_pages(res, inputs, total_count)
                    res = json.dumps(res, default=str)
                    rsp = Response(res, status=200, content_type='application/JSON')
                else:
                    rsp = Response("NOT FOUND", status=404, content_type='text/plain')

            elif inputs.method == 'POST':
                res = service.create(inputs.data)
                if res is not None:
                    values = list(map(str, res.values()))
                    key = "_".join(values)
                    headers = {"location": f"/products/{key}"}
                    rsp = Response("CREATED", status=201, content_type='text/plain', headers=headers)
                else:
                    rsp = Response("UNPROCESSABLE ENTITY", status=422, content_type='text/plain')

            else:
                rsp = Response("NOT IMPLEMENTED", status=501)
        else:
            rsp = Response("NOT FOUND", status=404, content_type='text/plain')

    except Exception as e:
        print(f"Path: /products\nException: {e}")
        rsp = Response("INTERNAL ERROR", status=500, content_type='text/plain')

    return rsp


@app.route('/products/<pid>', methods=["GET", "PUT", "DELETE"])
def get_products_by_pid(pid):
    try:
        inputs= rest_utils.RESTContext(request)
        service = _get_service_by_name("product_service")
        if service is not None:
            if inputs.method == 'GET':
                args = {}
                if inputs.args:
                    args = inputs.args
                args['pid'] = pid

                res, total_count = service.find_by_template(args, inputs.fields) # single product (no limits/offset)
                if res is not None:
                    res = _generate_product_links(res)
                    res = _generate_pages(res, inputs, total_count) # single product
                    res = json.dumps(res, default = str)
                    rsp = Response(res, status=200, content_type='application/JSON')
                else:
                    rsp = Response("NOT FOUND", status=404, content_type='text/plain')

            elif inputs.method == 'PUT':
                res = service.update(pid, inputs.data)
                if res is not None:
                    rsp = Response("OK", status=200, content_type='text/plain')
                else:
                    rsp = Response("NOT FOUND", status=404, content_type='text/plain')

            elif inputs.method == 'DELETE':
                res = service.delete({"pid": pid})
                if res is not None:
                    rsp = Response(f"Rows Deleted: {res['no_of_rows_deleted']}", status=204, content_type='text/plain')
                else:
                    rsp = Response("NOT FOUND", status=404, content_type='text/plain')

            else:
                rsp = Response("NOT IMPLEMENTED", status=501)

        else:
            rsp = Response("NOT FOUND", status=404, content_type='text/plain')

    except Exception as e:
        print(f"Path: /products/<pid>\nException: {e}")
        rsp = Response("INTERNAL ERROR", status=500, content_type='text/plain')

    return rsp


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)