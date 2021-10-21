import pymysql
import json
import logging

import middleware.context as context

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _get_db_connection():

    db_connect_info = context.get_db_info()

    logger.info("RDBService._get_db_connection:")
    logger.info("\t HOST = " + db_connect_info['host'])

    db_info = context.get_db_info()
    db_connection = pymysql.connect(
       **db_info
    )
    return db_connection


def get_by_prefix(db_schema, table_name, column_name, value_prefix):

    conn = _get_db_connection()
    cur = conn.cursor()

    sql = "select * from " + db_schema + "." + table_name + " where " + \
        column_name + " like " + "'" + value_prefix + "%'"
    print("SQL Statement = " + cur.mogrify(sql, None))

    res = cur.execute(sql)
    res = cur.fetchall()

    conn.close()

    return res


def _get_where_clause_args(template):

    terms = []
    args = []
    clause = None

    if template is None or template == {}:
        clause = ""
        args = None
    else:
        for k, v in template.items():
            terms.append(k + "=%s")
            args.append(v)

        clause = " where " + " AND ".join(terms)


    return clause, args


def find_by_template(db_schema, table_name, template, field_list):

    wc, args = _get_where_clause_args(template)

    conn = _get_db_connection()
    cur = conn.cursor()

    sql = "select * from " + db_schema + "." + table_name + " " + wc
    res = cur.execute(sql, args=args)
    res = cur.fetchall()

    conn.close()

    return res


def add_by_template(db_schema, table_name, template):
    columns = template.keys()
    columns_string = ', '.join(columns)

    values_string = []
    for v in template.values():
        if isinstance(v,int):
            values_string.append(v)
        else:
            values_string.append("'"+v+"'")

    values_string = ", ".join(values_string)

    conn = _get_db_connection()
    cur = conn.cursor()

    sql = f"insert into {db_schema}.{table_name} ({columns_string})" \
          f" values ({values_string});"
    res = cur.execute(sql)
    id = conn.insert_id()
    conn.commit()
    conn.close()

    return id


def update_by_template(db_schema, table_name, update_template, where_template):
    update_list = []
    for k, v in update_template.items():
        if isinstance(v, int):
            update_list.append(f"{k} = {v}")
        else:
            update_list.append(f"{k} = '{v}'")

    update_string = ', '.join(update_list)

    where_list = []
    for k, v in where_template.items():
        if isinstance(v, int):
            where_list.append(f"{k} = {v}")
        else:
            where_list.append(f"{k} = '{v}'")

    where_string = ', '.join(where_list)

    conn = _get_db_connection()
    cur = conn.cursor()

    sql = f"UPDATE {db_schema}.{table_name} SET {update_string} WHERE {where_string};"
    res = cur.execute(sql)
    conn.commit()
    conn.close()
    return res


def delete_by_template(db_schema, table_name, template):
    where_list = []
    for k, v in template.items():
        if isinstance(v, int):
            where_list.append(f"{k} = {v}")
        else:
            where_list.append(f"{k} = '{v}'")
    where_string = ' AND '.join(where_list)

    conn = _get_db_connection()
    cur = conn.cursor()

    sql1 = f"DELETE FROM {db_schema}.{table_name} where {where_string};"
    # sql2 = "SELECT row_count() as no_of_rows_deleted;"
    cur.execute(sql1)
    # cur.execute(sql2)
    # res = cur.fetchone()
    res = cur.rowcount
    conn.commit()
    conn.close()
    return res
