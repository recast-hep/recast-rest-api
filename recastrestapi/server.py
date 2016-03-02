import recastdb.models
from recastdb.database import db

from eve import Eve
from eve.auth import BasicAuth
from eve_sqlalchemy import SQL
from eve_sqlalchemy.validation import ValidatorSQL
from eve_sqlalchemy.decorators import registerSchema
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

from recastrestapi.apiconfig import config as apiconf

from settings import DOMAIN, SQLALCHEMY_DATABASE_URI, DEBUG, XML, JSON, RESOURCE_METHODS, PUBLIC_ITEM_METHODS, HATEOAS, IF_MATCH, LAST_UPDATED, DATE_CREATED, ID_FIELD, ITEM_LOOKUP_FIELD

class TokenAuth(BasicAuth):
    def check_auth(self, orcid_id, token, allowed_roles, resource, method):
        """ 
            Token based authentications 
        """
        try:
            user = recastdb.models.User.query.filter(recastdb.models.User.orcid_id == orcid_id).one()
            
            access_token = recastdb.models.AccessToken.query.filter(recastdb.models.AccessToken.token == token).one()
            return access_token.user_id == user.id
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
    'RESOURCE_METHODS': RESOURCE_METHODS,
    'PUBLIC_ITEM_METHODS': PUBLIC_ITEM_METHODS,
    'HATEOAS': HATEOAS,
    'IF_MATCH': IF_MATCH,
    'LAST_UPDATED': LAST_UPDATED,
    'DATE_CREATED': DATE_CREATED,
    'ID_FIELD': ID_FIELD,
    'ITEM_LOOKUP_FIELD': ITEM_LOOKUP_FIELD,
}

app = Eve(auth=TokenAuth, settings=SETTINGS, validator=ValidatorSQL, data=SQL)

Base = recastdb.database.db.Model

#bind SQLAlchemy
db = app.data.driver
Base.metadata.bind = db.engine
db.Model = Base()
db.create_all()
