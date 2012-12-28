import os
from ConfigParser import SafeConfigParser

from . import ec2.config

def configure(config_file=None):
    if not config_file:
        config_file = ['/etc/awsdeploy', os.path.expanduser('~/.awsconfig')]

    conf = SafeConfigParser() 
    if conf.read(config_file):
        ec2.config.aws_access_key_id = conf.get('awsdeploy',
                                                'aws_access_key_id')
        ec2.config.aws_secret_key = conf.get('awsdeploy', 'aws_secret_key')
        ec2.config.region = conf.get('awsdeploy', 'region')
