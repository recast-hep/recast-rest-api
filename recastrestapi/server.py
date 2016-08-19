import recastdb.models
from recastdb.database import db

from eve import Eve
from eve_sqlalchemy import SQL
from eve_sqlalchemy.validation import ValidatorSQL

from settings import DOMAIN, SQLALCHEMY_DATABASE_URI, DEBUG, PAGINATION_DEFAULT
from settings import XML, JSON, RESOURCE_METHODS, PUBLIC_METHODS, ITEM_METHODS
from settings import PUBLIC_ITEM_METHODS, HATEOAS, IF_MATCH, ID_FIELD, ITEM_LOOKUP_FIELD
from settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME
from settings import TokenAuth

from boto3.session import Session
import requests as httprequest
import json

SETTINGS = {
	'PAGINATION_DEFAULT':PAGINATION_DEFAULT,
	'DOMAIN': DOMAIN,
	'SQLALCHEMY_DATABASE_URI': SQLALCHEMY_DATABASE_URI,
	'DEBUG': DEBUG,
	'XML': XML,
	'JSON': JSON,
	'RESOURCE_METHODS': RESOURCE_METHODS,
	'ITEM_METHODS': ITEM_METHODS,
	'PUBLIC_METHODS': PUBLIC_METHODS,
	'PUBLIC_ITEM_METHODS': PUBLIC_ITEM_METHODS,
	'HATEOAS': HATEOAS,
	'IF_MATCH': IF_MATCH,
	'ID_FIELD': ID_FIELD,
	'ITEM_LOOKUP_FIELD': ITEM_LOOKUP_FIELD,
	'SQLALCHEMY_TRACK_MODIFICATIONS': True
}

def pre_request_archives_post_callback(request, lookup=None):
	print type(request.files),request.files
	print type(request.data),request.data
	print type(request.form),request.form
	print type(request.json),request.json
	print dir(request)

	upload_with_tag(request,'request')

def pre_response_archives_post_callback(request, lookup=None):
	upload_with_tag(request,'response')

import uuid
import werkzeug.datastructures
def upload_with_tag(request,tag):
	"""
		Uploads File file to AWS s3 with tag (either request or response)
	"""

	print 'UPLOAD!'

	zip_file = request.files.get('file')
	request.files = werkzeug.datastructures.ImmutableMultiDict({})
	orcid_id = request.__dict__['authorization']['username']


	print 'UPLOAD!',zip_file

	if zip_file:
		print "HELL YEAH"
		print request.form
		aws_filename = str(uuid.uuid4())
		modified_form = request.form.to_dict()
		print modified_form.update(file_name = aws_filename)
		print "------"
		request.form = werkzeug.datastructures.ImmutableMultiDict(
			modified_form
		)

	if zip_file:
		metadata = {'tag': tag,
					'username': orcid_id,
					'originalname': zip_file.filename,
					}
		print 'UPLOAD!',zip_file,'with',metadata
		upload_AWS(zip_file, aws_filename, metadata)
	print 'DONE!'

def upload_AWS(zip_file, file_uuid, metadata=None):
	session = Session(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
	s3 = session.resource('s3')
	s3.Bucket(AWS_S3_BUCKET_NAME).put_object(
		Key=str(file_uuid),
		Body=zip_file,
		ACL='public-read',
		Metadata=metadata)

def download_AWS(file_name, original_file_name, download_path=None):
	session = Session(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
	s3 = session.resource('s3')
	out_file = download_path or original_file_name
	s3.Bucket(AWS_S3_BUCKET_NAME).download_file(file_name, out_file)

def after_fetch_archives(request, lookup=None):
	""" Function to add download link in the response """
	print 'CALLED'

	url = 'https://s3.amazonaws.com/{}/{}'.format(AWS_S3_BUCKET_NAME, request['file_name'])
	r = httprequest.get(url)
	if r.ok:
		request['file_link'] = url
	else:
		request['file_link'] = ''


app = Eve(auth=TokenAuth, settings=SETTINGS, validator=ValidatorSQL, data=SQL)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

app.on_pre_POST_request_archives      += pre_request_archives_post_callback
app.on_fetched_item_request_archives  += after_fetch_archives

app.on_pre_POST_response_archives 	  += pre_response_archives_post_callback
app.on_fetched_item_response_archives += after_fetch_archives

Base = recastdb.database.db.Model

#bind SQLAlchemy
db = app.data.driver
Base.metadata.bind = db.engine
db.Model = Base()
