import pymysql
import traceback
from .celery import app
from .login_task.login import AccountLogin

MYSQL_HOST = 'rm-uf6uv29790jnj85iw.mysql.rds.aliyuncs.com'
MYSQL_PORT = 3306
MYSQL_USER = 'xiangchen'
MYSQL_PASSWORD = 'Pl1996317'
MYSQL_DB = 'weibo_spider'
MYSQL_CHARSET = 'utf8mb4'


@app.task
def task(username, password):
    try:
        cookies_jar = AccountLogin(username, password).process()
    except:
        traceback.print_exc()
    else:
        cookies_str = '; '.join([cookie.name + '=' + cookie.value for cookie in cookies_jar])
        sql = 'update cookie_pool_wb set cookies=%s, code=%s where username=%s'
        conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB, charset=MYSQL_CHARSET)
        cur = conn.cursor()
        cur.execute(sql, (cookies_str, 1, username))
        conn.commit()
        cur.close()
        conn.close()
        return True
