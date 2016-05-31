from setuptools import setup, find_packages

setup(
    name = 'recast-rest-api',
    description = 'API for the RECAST project',
    url = 'https://github.com/cbora/recast-rest-api',
    author = 'Christian Bora',
    author_email = 'borachristian@gmail.com',
    packages = find_packages(),
    include_package_data = True,
    install_requires = [
        'Flask==0.10.1',
        'werkzeug==0.10.4',
        'Eve==0.5.3',
        'eve-sqlalchemy',
        'celery',
        'pyyaml',
        'IPython',
        'psycopg2',
        'click',
        'boto3',
        'requests',
        'recast-database'
        ],
    entry_points = {
        'console_scripts': [
            'recast-api = recastrestapi.apicli:apicli',
            'recast-api-admin = recastrestapi.admincli:admincli',
            ]
        },
    dependency_links = [
        'https://github.com/recast-hep/recast-database/tarball/master#egg=recast-database-0.0.1',
        ]
    )
    
