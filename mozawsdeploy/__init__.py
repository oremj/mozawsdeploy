import os
from ConfigParser import SafeConfigParser

from .ec2 import config as ec2_config

def configure(config_file=None):
    if not config_file:
        config_file = ['/etc/awsdeploy', os.path.expanduser('~/.awsconfig')]

    conf = SafeConfigParser() 
    if conf.read(config_file):
        ec2_config.aws_access_key_id = conf.get('awsdeploy',
                                                'aws_access_key_id')
        ec2_config.aws_secret_access_key = conf.get('awsdeploy',
                                                    'aws_secret_access_key')
        ec2_config.region = conf.get('awsdeploy', 'region')
