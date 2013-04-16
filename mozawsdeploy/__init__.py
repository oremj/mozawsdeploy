import os
from ConfigParser import SafeConfigParser

from . import config


def configure(config_file=None, access_only=False):
    """Access only is for running the puppet ext node classifier"""
    if not config_file:
        config_file = ['/etc/awsdeploy',
                       '/etc/awsdeploy.puppet',
                       os.path.expanduser('~/.awsconfig')]

    conf = SafeConfigParser()
    if conf.read(config_file):
        config.aws_access_key_id = conf.get('awsdeploy',
                                            'aws_access_key_id')
        config.aws_secret_access_key = conf.get('awsdeploy',
                                                'aws_secret_access_key')
        if not access_only:
            config.app = conf.get('awsdeploy', 'app')
            config.env = conf.get('awsdeploy', 'env')
            config.region = conf.get('awsdeploy', 'region')
            config.puppet_host = conf.get('awsdeploy', 'puppet_host')
            config.vpc_id = conf.get('awsdeploy', 'vpc_id')
