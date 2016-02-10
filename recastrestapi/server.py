import recastdb.models
from recastdb.database import db

from eve import Eve
from eve_sqlalchemy import SQL
from eve_sqlalchemy.validation import ValidatorSQL
from eve_sqlalchemy.decorators import registerSchema

from recastrestapi.apiconfig import config as apiconf

registerSchema('users')(recastdb.models.User)
registerSchema('analysis')(recastdb.models.Analysis)
registerSchema('subscriptions')(recastdb.models.Subscription)

SETTINGS = {
    'DEBUG': True,
    'SQLALCHEMY_DATABASE_URI': apiconf['DBPATH'],
    'DOMAIN': {
        'users': recastdb.models.User._eve_schema['users'],
        'analysis': recastdb.models.Analysis._eve_schema['analysis'],
        'subscriptions': recastdb.models.Subscription._eve_schema['subscriptions'],
        }
}

app = Eve(auth=None, settings=SETTINGS, validator=ValidatorSQL, data=SQL)

Base = recastdb.database.db.Model

#bind SQLAlchemy
db = app.data.driver
Base.metadata.bind = db.engine
db.Model = Base()
db.create_all()


