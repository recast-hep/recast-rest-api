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

from settings import DOMAIN, SQLALCHEMY_DATABASE_URI, DEBUG
from settings import XML, JSON, RESOURCE_METHODS, PUBLIC_METHODS
from settings import PUBLIC_ITEM_METHODS, HATEOAS, IF_MATCH, ID_FIELD, ITEM_LOOKUP_FIELD
from settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME
from settings import ZENODO_ACCESS_TOKEN

from eve.io.media import MediaStorage
from boto3.session import Session
import requests as httprequest
import json

class TokenAuth(BasicAuth):
    def check_auth(self, orcid_id, token, allowed_roles, resource, method):
        """ 
            Token based authentications 
        """        
        try:
            user = recastdb.models.User.query.filter(
                recastdb.models.User.orcid_id == orcid_id).one()
            access_token = recastdb.models.AccessToken.query.filter(
                recastdb.models.AccessToken.token == token).one()
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
    'PUBLIC_METHODS': PUBLIC_METHODS,
    'PUBLIC_ITEM_METHODS': PUBLIC_ITEM_METHODS,
    'HATEOAS': HATEOAS,
    'IF_MATCH': IF_MATCH,
    'ID_FIELD': ID_FIELD,
    'ITEM_LOOKUP_FIELD': ITEM_LOOKUP_FIELD,
}

def pre_request_archives_post_callback(request, lookup=None):
    zip_file = request.files.get('file')
    if zip_file:
        upload_AWS(zip_file, request.form['file_name'])
    """
        if request.args.has_key('deposition_id'):
            deposition_id = request.args.get('deposition_id')
            file_id = upload_zenodo(deposition_id, request.form['file_name'], zip_file)
            request_form['zenodo_file_id'] = file_id
    """        

def pre_archives_get_callback(request, lookup=None):
    """ download file for request archive
        used for response archive too
    """
    try:
        if request.args.has_key('download'):
            file_name = json.loads(lookup.__dict__['response'][0])['file_name']
            original_file_name = json.loads(lookup.__dict__['response'][0])['original_file_name']
            path = None
            if request.args.has_key('path'):
                path = request.args.get('path')
            download_AWS(file_name, original_file_name, path)
    except Exception, e:
        # to handle requests from the web interface
        print json.dumps(lookup.__dict__['response'][0])
        print "nothing"
        return


def pre_request_post_callback(request, lookup=None):
    """ creating depositions for request """
    username = request.args['username']
    orcid_id = request.__dict__['authorization']['username']
    request_uuid = request.form['uuid']
    description = request.form['description']
    deposition_id = create_depostion(username, 
                                     orcid_id, 
                                     request_uuid, 
                                     description)
    request_form['zenodo_deposition_id'] = deposition_id

def pre_response_archives_post_callback(request, lookup=None):
    zip_file = request.files.get('file')
    if zip_file:
        upload_AWS(zip_file, request.form['file_name'])
        
def upload_AWS(zip_file, file_uuid):
    session = Session(AWS_ACCESS_KEY_ID,
                 AWS_SECRET_ACCESS_KEY)
    s3 = session.resource('s3')
    s3.Bucket(AWS_S3_BUCKET_NAME).put_object(
        Key=str(file_uuid), Body=zip_file, ACL='public-read')

def download_AWS(file_name, original_file_name, download_path=None):
    session = Session(AWS_ACCESS_KEY_ID,
                      AWS_SECRET_ACCESS_KEY)
    s3 = session.resource('s3')
    out_file = download_path or original_file_name
    s3.Bucket(AWS_S3_BUCKET_NAME).download_file(file_name, out_file)

def create_deposition(username, orcid_id, request_uuid, description):
    url = 'https://zenodo.org/api/api/depositions/?access_token={}'.format(
        ZENODO_ACCESS_TOKEN)
    description = 'Recast_request: {} Requester: {} ORCID: {} Request_description: {}'.format(
        request_uuid, username, orcid_id, description)
    headers = {"Content-Type": "application/json"}
    deposition_data = {"metadata":
                           {
            "access_right": "embargoed",
            "upload_type": "dataset",
            "creators": [{"name": "Bora, Christian"}],
            "description": description,
            "title": "Sample title"
            }
                       }
    response = httprequest.post(url, data=json.dumps(deposition_data), headers=headers)
    return response.json()['id']

def upload_zenodo(deposition_id, file_uuid, zip_file):
    url = 'https://zenodo.org/api/deposit/depositions/{}/files?access_token={}'.format(
        deposition_id, ZENODO_ACCESS_TOKEN)
    json_data_file = {"filename": file_uuid}
    response = httprequest.post(url, data=json_data_file, files=zip_file)
    return response.json()['id']

def before_insert_archives(request, lookup=None):
    try:
        #delete the recast_file filestorage object(not entered in db)
        del request[0]['file']
    except Exception, e:
        pass

app = Eve(auth=TokenAuth, settings=SETTINGS, validator=ValidatorSQL, data=SQL)

app.on_pre_GET_request += pre_request_post_callback

app.on_pre_POST_request_archives += pre_request_archives_post_callback
app.on_post_GET_request_archives += pre_archives_get_callback

app.on_pre_POST_response_archives += pre_response_archives_post_callback
app.on_post_GET_response_archives += pre_archives_get_callback

app.on_insert_request_archives += before_insert_archives
app.on_insert_response_archives += before_insert_archives
Base = recastdb.database.db.Model

#bind SQLAlchemy
db = app.data.driver
Base.metadata.bind = db.engine
db.Model = Base()
db.create_all()
