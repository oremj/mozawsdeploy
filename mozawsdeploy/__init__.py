import os
from ConfigParser import SafeConfigParser

from . import config


def configure(config_file=None):
    if not config_file:
        config_file = ['/etc/awsdeploy', os.path.expanduser('~/.awsconfig')]

    conf = SafeConfigParser()
    if conf.read(config_file):
        config.aws_access_key_id = conf.get('awsdeploy',
                                            'aws_access_key_id')
        config.aws_secret_access_key = conf.get('awsdeploy',
                                                'aws_secret_access_key')
        config.region = conf.get('awsdeploy', 'region')
        config.puppet_ip = conf.get('awsdeploy', 'puppet_ip')
        config.subnet_id = conf.get('awsdeploy', 'subnet_id')
        config.vpc_id = conf.get('awsdeploy', 'vpc_id')
