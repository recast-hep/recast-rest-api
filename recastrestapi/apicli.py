import click
import os
import subprocess

@click.group()
def apicli():
    pass

@apicli.command()
@click.option('--config', '-c')
def server(config):
    if config:
        os.environ['RECASTCONTROLCENTER_CONFIG'] = config
    from server import app
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
