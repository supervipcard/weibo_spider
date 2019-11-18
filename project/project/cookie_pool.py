from scrapy.utils.project import get_project_settings
from sqlalchemy import create_engine
import random


class CookiePool(object):
    def __init__(self):
        settings = get_project_settings()
        self.mysql_engine = create_engine(settings['MYSQL_KEY'], pool_size=settings['MYSQL_POOL_SIZE'], pool_recycle=settings['MYSQL_POOL_RECYCLE'], pool_timeout=settings['MYSQL_POOL_TIMEOUT'])

    def select(self):
        sql = 'select username, password, cookies from cookie_pool_wb where code=%s'
        with self.mysql_engine.connect() as conn:
            cur = conn.execute(sql, (1,))
            result = cur.fetchall()
        if result:
            return random.choice(result)

    def update_code(self, username, code):
        sql = 'update cookie_pool_wb set code=%s where username=%s'
        with self.mysql_engine.connect() as conn:
            conn.execute(sql, (code, username))
