import os, pymysql
from Services.ProductService.product_service import ProductService as ProductService
from middleware import context as ctx

default_limit = ctx.get_context_value("MAX_TABLE_ROWS_TO_PRINT")

def get_db_info():
    db_host = os.environ.get("DBHOST", None)
    db_user = os.environ.get("DBUSER", None)
    db_password = os.environ.get("DBPASSWORD", None)

    if db_host is not None:
        db_info = {
            "host": db_host,
            "user": db_user,
            "password": db_password,
            "cursorclass": pymysql.cursors.DictCursor
        }
    else:
        db_info = {
            "host": "localhost",
            "user": "dbuser",
            "password": "dbuserdbuser",
            "cursorclass": pymysql.cursors.DictCursor
        }

    return db_info


def _get_service_by_name(service_name):
    if service_name == "product_service":
        db_info = get_db_info()
        del db_info['cursorclass']
        db_info['db'] = "ProductDB"

        return ProductService({
            "db_name": "ProductDB",
            "table_name": "Products",
            "db_connect_info": db_info,
            "key_columns": ['pid']
        })


def _generate_product_links(res):
    new_res = []
    for product_dict in res:
        links = [{
            "rel": "self",
            "href": f"/products/{product_dict['pid']}"
        }]
        product_dict['links'] = links
        new_res.append(product_dict)

    return new_res




def _generate_pages(res, inputs, total_count):
    path = inputs.path
    prev_url = f"{path}?"
    next_url = f"{path}?"

    args = []
    for k,v in inputs.args.items():
        args.append(f"{k}={v}")
    args = '&'.join(args)

    if args:
        prev_url += f"{args}"
        next_url += f"{args}"

    if inputs.fields:
        prev_url += f"&fields={inputs.fields}"
        next_url += f"&fields={inputs.fields}"

    limit = int(inputs.limit) if inputs.limit else default_limit
    if limit:
        prev_url += f"&limit={limit}"
        next_url += f"&limit={limit}"

    if inputs.order_by:
        prev_url += f"&order_by={inputs.order_by}"
        next_url += f"&order_by={inputs.order_by}"

    offset = int(inputs.offset) if inputs.offset else 0
    if offset > 0 and offset + limit >= total_count: # no more results
        prev_url += f"&offset={offset-limit}"
        next_url = ""
    elif offset == 0 and offset + limit < total_count:
        next_url += f"&offset={offset+limit}"
        prev_url = ""
    elif offset == 0 and offset + limit >= total_count:
        next_url = ""
        prev_url = ""
    else:
        prev_url += f"&offset={offset - limit}"
        next_url += f"&offset={offset + limit}"

    new_dict = {
        "data": res,
        "links": [
            {
                "rel": "self",
                "href": inputs.url
            },
            {
                "rel": "next",
                "href": next_url
            },
            {
                "rel": "prev",
                "href": prev_url
            }
        ]
    }

    return new_dict