import pymysql
import traceback
from .celery import app
from .login_task.login import AccountLogin

MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_USER = 'test'
MYSQL_PASSWORD = 'test123'
MYSQL_DB = 'test'


@app.task
def task(username, password):
    try:
        cookies_jar = AccountLogin(username, password).process()
    except:
        traceback.print_exc()
    else:
        cookies_str = '; '.join([cookie.name + '=' + cookie.value for cookie in cookies_jar])
        sql = 'update cookie_pool_wb set cookies=%s, code=%s where username=%s'
        conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB, charset='utf8')
        cur = conn.cursor()
        cur.execute(sql, (cookies_str, 1, username))
        conn.commit()
        cur.close()
        conn.close()
        return True
