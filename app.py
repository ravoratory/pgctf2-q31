from bottle import app as bottleapp
from bottle import route, run, template, request, redirect, Response
from bottle import jinja2_template as template

from beaker.middleware import SessionMiddleware
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from uuid import uuid4
import sqlite3
import subprocess

DATABASE = './database.db'

cache_opts = {
    'cache.type': 'file',
    'cache.data_dir': './cache/data',
    'cache.lock_dir': './cache/lock'
}

cache = CacheManager(**parse_cache_config_options(cache_opts))
session_opts = {
    'session.type': 'file',
    'session.data_dir': './data',
    'session.auto': True,
}

bottle_app = bottleapp()
app = SessionMiddleware(bottleapp(), session_opts)

flag = "flag is secret :)"

@route('/', method=['GET'])
def index():
    return template('index', token=str(uuid4()))


@route('/admin')
def admin():
    session = request.environ.get("beaker.session")
    message = flag if "admin" in session else ""
    return template('admin', message=message)


@route('/preview', method=["GET", "POST"])
@cache.cache('cache_func', expire=60)
def preview():
    if request.method == "GET":
        return Response("ok", 200)
    else:
        name = request.forms.get("name", "").replace("'", "''").replace('\\', '')
        body = request.forms.get("body", "").replace("'", "''").replace('\\', '')
        role = request.query.get("role", "angel")
        stat_id = uuid4()
        con = get_db()
        con.execute(f"insert into reflection(id, name, body) values('{stat_id}', '{name}', '{body}')")
        con.commit()
        con.close()
        return template('preview', name=name, body=body, stat_id=stat_id, role=role)


@route('/report/<report_id>', method=["GET", "POST"])
def report(report_id):
    if request.method == "GET":
        con = get_db()
        data = list(con.execute(f"select name, body from reflection where id='{report_id}'"))
        con.close()
        if len(data)== 0:
            return "", 404
        name, body = data[0]
        return template('report', name=name, body=body)
    else:
        stat_id = request.forms.get("stat_id", "")
        # crawling
        subprocess.Popen(["python3", "./angel.py", f"{stat_id}"])
        redirect(f'/report/{report_id}')
        
@route('/report/<report_id>/reply', method="POST")
def reply(report_id):
        con = get_db()
        data = list(con.execute(f"select id, name, body from reflection where id='{report_id}'"))
        if len(data)== 0:
            return "", 404
        stat_id, name, body = data[0]
        body += request.body.read().decode().replace("'", "''").replace("\\", "")
        con.execute(f"update reflection set body='{body}' where id='{stat_id}'")
        con.commit()
        con.close()
        return Response("ok", 200)

def get_db():
    db = sqlite3.connect(DATABASE)
    return db

if __name__ == "__main__":
    run(app=app, host='localhost', port=8031, reloader=True)
