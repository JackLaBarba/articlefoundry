from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import create_session
from sqlalchemy.ext.declarative import declarative_base

ai_ro_info = {
    'user': 'ai_ro',
    'password': '',
    'host': 'sfo-db01.int.plos.org',
    'port': 3306,
    'database': 'ai_stage',
}

Base = declarative_base()
engine = create_engine('mysql+mysqldb://%(user)s:%(password)s@%(host)s:%(port)s/%(database)s' % ai_ro_info)
metadata = MetaData(bind=engine)

class Article(Base):
    __table__ = Table('articleflow_article', metadata, autoload=True)

class AIapi(object):

    def __init__(self):
        self.session = create_session(bind=engine)

    def __enter__(self):
        self.__init__()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.session.close()

    def get_si_guid(self, doi):
        try:
            a = self.session.query(Article).filter(Article.doi == doi).first()
            return a.si_guid
        except AttributeError, e:
            raise KeyError("Unable to find article with DOI, %s, in AI's database" % doi)



