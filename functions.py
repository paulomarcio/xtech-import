import pymysql
import http.client
import json
import settings


# Método para efetuar GET com cURL
def api_get(action):
    conn = http.client.HTTPConnection(settings.endpoint, timeout=120)

    headers = {
        'content-type': "application/json",
        'x-api-key': settings.api_key,
        'x-app-key': settings.app_key
    }

    conn.request("GET", action, headers=headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))


# Método para efetuar PUT com cURL
def api_put(action, params):
    conn = http.client.HTTPConnection(settings.endpoint, timeout=120)

    payload = json.dumps(params, ensure_ascii=False)

    headers = {
        'content-type': "application/json",
        'x-api-key': settings.api_key,
        'x-app-key': settings.app_key
    }

    conn.request("PUT", action, payload, headers=headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))


# Método para efetuar conexão ao banco de dados local
def mysql_connect():
    # Open database connection
    db = pymysql.connect(settings.db_host, settings.db_user, settings.db_password, settings.db_name)
    return db


# Método para recuperar o IDs do produto informado pelo SKU
def get_produto(sku):
    # Open database connection
    db = mysql_connect()

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # execute SQL query using execute() method.
    cursor.execute("SELECT * FROM produtos WHERE codigo_lynx = '%s'" % sku)

    # Fetch a single row using fetchone() method.
    data = cursor.fetchone()

    # disconnect from server
    db.close()

    return data


def get_imagens_produto(produto_id):
    # Open database connection
    db = mysql_connect()

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # execute SQL query using execute() method.
    cursor.execute("SELECT * FROM imagens WHERE produto_id = %s" % produto_id)

    # Fetch a single row using fetchone() method.
    data = cursor.fetchall()

    # disconnect from server
    db.close()

    return data
