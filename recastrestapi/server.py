import recastdb.models
from recastdb.database import db

from eve import Eve
from eve.auth import TokenAuth
from eve_sqlalchemy import SQL
from eve_sqlalchemy.validation import ValidatorSQL
from eve_sqlalchemy.decorators import registerSchema

from recastrestapi.apiconfig import config as apiconf
from settings import DOMAIN, SQLALCHEMY_DATABASE_URI, DEBUG, XML, JSON


class TokenAuth(TokenAuth):
    def check_auth(self, token, allowed_roles, resource, method):
        """ 
            Token based authentications 
        """
        #accounts = app.data.driver.db['accounts']
        return accounts.find_one({'token': token})

SETTINGS = {
    'DOMAIN': DOMAIN,
    'SQLALCHEMY_DATABASE_URI': SQLALCHEMY_DATABASE_URI,
    'DEBUG': DEBUG,
    'XML': XML,
    'JSON': JSON,
}

app = Eve(auth=None, settings=SETTINGS, validator=ValidatorSQL, data=SQL)

Base = recastdb.database.db.Model

#bind SQLAlchemy
db = app.data.driver
Base.metadata.bind = db.engine
db.Model = Base()
db.create_all()


