import pymysql
import traceback
from .celery import app
from .login_task.login import AccountLogin
from .settings import *


@app.task
def task(username, password):
    try:
        account_login = AccountLogin(username, password)
        cookies_jar = account_login.process()
    except:
        traceback.print_exc()
    else:
        check_result = account_login.check()
        if "$CONFIG['uid']=" in check_result:
            cookies_str = '; '.join([cookie.name + '=' + cookie.value for cookie in cookies_jar])
            sql = 'update cookie_pool_wb set cookies=%s, code=%s where username=%s'
            conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB, charset=MYSQL_CHARSET)
            cur = conn.cursor()
            cur.execute(sql, (cookies_str, 1, username))
            conn.commit()
            cur.close()
            conn.close()
            return '账号正常({})'.format(username)
        else:
            sql = 'update cookie_pool_wb set code=%s where username=%s'
            conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB, charset=MYSQL_CHARSET)
            cur = conn.cursor()
            cur.execute(sql, (-3, username))
            conn.commit()
            cur.close()
            conn.close()
            return '账号异常({})'.format(username)
