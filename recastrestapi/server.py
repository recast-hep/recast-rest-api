import recastdb.models
from recastdb.database import db

from eve import Eve
from eve.auth import TokenAuth
from eve_sqlalchemy import SQL
from eve_sqlalchemy.validation import ValidatorSQL
from eve_sqlalchemy.decorators import registerSchema
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

from recastrestapi.apiconfig import config as apiconf
from settings import DOMAIN, SQLALCHEMY_DATABASE_URI, DEBUG, XML, JSON


class TokenAuth(TokenAuth):
    def check_auth(self, token, allowed_roles, resource, method):
        """ 
            Token based authentications 
        """
        try:
            recastdb.models.AccessToken.query.filter(recastdb.models.AccessToken.token == token).one()
            return True
        except MultipleResultsFound, e:
            return False
        except NoResultFound, e:
            return False
            
SETTINGS = {
    'DOMAIN': DOMAIN,
    'SQLALCHEMY_DATABASE_URI': SQLALCHEMY_DATABASE_URI,
    'DEBUG': DEBUG,
    'XML': XML,
    'JSON': JSON,
}

app = Eve(auth=TokenAuth, settings=SETTINGS, validator=ValidatorSQL, data=SQL)

Base = recastdb.database.db.Model

#bind SQLAlchemy
db = app.data.driver
Base.metadata.bind = db.engine
db.Model = Base()
db.create_all()
