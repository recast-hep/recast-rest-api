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
from settings import ZENODO_ACCESS_TOKEN, MY_HOST

from eve.io.media import MediaStorage
from boto3.session import Session
import requests as httprequest
import json
import urllib

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
    'SQLALCHEMY_TRACK_MODIFICATIONS': True
}

def pre_request_archives_post_callback(request, lookup=None):
    """
        Uploads Request file to AWS s3
    """
    zip_file = request.files.get('file')
    if zip_file:
        username = ''
        orcid_id = ''
        description = ''
        title = ''
        metadata = {'title': title,
                    'owner': username,
                    'orcid_id': orcid_id,
                    'description': description
                    }
        upload_AWS(zip_file, request.form['file_name'], metadata)

def pre_response_archives_post_callback(request, lookup=None):
    """ 
       Uploads Response file to AWS S3
 
   """
    zip_file = request.files.get('file')
    if zip_file:
        upload_AWS(zip_file, request.form['file_name'])
        
def upload_AWS(zip_file, file_uuid, metadata=None):
    session = Session(AWS_ACCESS_KEY_ID,
                 AWS_SECRET_ACCESS_KEY)
    s3 = session.resource('s3')
    s3.Bucket(AWS_S3_BUCKET_NAME).put_object(
        Key=str(file_uuid), 
        Body=zip_file, 
        ACL='public-read',
        Metadata=metadata)

def download_AWS(file_name, original_file_name, download_path=None):
    session = Session(AWS_ACCESS_KEY_ID,
                      AWS_SECRET_ACCESS_KEY)
    s3 = session.resource('s3')
    out_file = download_path or original_file_name
    s3.Bucket(AWS_S3_BUCKET_NAME).download_file(file_name, out_file)

def create_deposition(requester_id, request_uuid, description):
    url = 'https://zenodo.org/api/api/depositions/?access_token={}'.format(
        ZENODO_ACCESS_TOKEN)
    username = None
    orcid_id = None
    user_url = '{}/{}'.format(MY_HOST, requester_id)
    response = httprequest.get(url)
    if response.ok:
        username = response['name']
        orcid_id = response['orcid_id']
        
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

def before_insert_request(request, lookup=None):
    '''
       Function called before inserting request to DB
         use it to create a Zenodo deposition and update the json
    '''
    deposition_id = create_deposition(request['requester_id'], 
                                      request['uuid'],
                                      request['reason_for_request']
                                      )
    request['zenodo_deposition_id'] = deposition_id
    
def before_insert_archives(request_data, lookup=None):
    try:
        #delete the recast_file filestorage object(not entered in db)
        for request in request_data:
            if request.has_key('deposition_id'):
                request['zenodo_file_id'] = upload_zenodo(deposition_id=request['deposition_id'],
                                                          file_uuid=request['file_name'], 
                                                          zip_file=request['file']
                                                          )
                del request['deposition_id']
            del request['file']
    except Exception, e:
        pass


def after_fetch_archives(request, lookup=None):
    url = 'https://s3.amazonaws.com/{}/{}'.format(
        AWS_S3_BUCKET_NAME, request['file_name'])
    r = httprequest.get(url)
    if r.ok:
        request['file_link'] = url
    else:
        request['file_link'] = ''


app = Eve(auth=TokenAuth, settings=SETTINGS, validator=ValidatorSQL, data=SQL)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


app.on_insert_request += before_insert_request

app.on_pre_POST_request_archives += pre_request_archives_post_callback
app.on_fetched_item_request_archives += after_fetch_archives

app.on_fetched_item_response_archives += after_fetch_archives
app.on_pre_POST_response_archives += pre_response_archives_post_callback

app.on_insert_request_archives += before_insert_archives
app.on_insert_response_archives += before_insert_archives

Base = recastdb.database.db.Model

#bind SQLAlchemy
db = app.data.driver
Base.metadata.bind = db.engine
db.Model = Base()
db.create_all()
