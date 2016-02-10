import click
import Ipython
import os
import yaml

@click.group()
def admincli():
    pass

@admincli.command()
@click.option('--config', '-c')
def mk_config(output):
    config_data = {}
    for k,v in os.environ.iteritems():
        if k.startswith('RECAST_'):
            config_data[k.replace('RECAST_','')] = v
    with open(output, 'w') as outputfile:
        outfile.write(yaml.dump(config_data,default_flow_style=False))
