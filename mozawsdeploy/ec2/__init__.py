import os
import time

from boto.ec2 import connect_to_region, elb

from . import gen_user_data
from .. import config


def get_connection():
    c = connect_to_region(config.region,
                          aws_access_key_id=config.aws_access_key_id,
                          aws_secret_access_key=config.aws_secret_access_key)

    return c


def get_elb_connection():
    c = elb.connect_to_region(config.region,
                              aws_access_key_id=config.aws_access_key_id,
                              aws_secret_access_key=config.aws_secret_access_key)

    return c


def get_instance(instance_ids=None, filters=None):
    """Returns the first instance returned by filters"""
    c = get_connection()
    reservations = c.get_all_instances(instance_ids=instance_ids,
                                       filters=filters)

    for r in reservations:
        for i in r.instances:
            return i


def create_server(name, app, server_type, env, ami,
                  security_groups=None, security_group_ids=None, 
                  userdata=None, subnet_id=config.subnet_id,
                  count=1, key_name=None):

    if not userdata:
        userdata = [gen_user_data.init(),
                    gen_user_data.yum_install(['puppet', 'git']),
                    gen_user_data.easy_install('pip'),
                    gen_user_data.pyrepo_install(['supervisor', 'virtualenv']),
                    gen_user_data.add_host(config.puppet_ip, 'puppet'),
                    gen_user_data.run_puppet()]
        userdata = "\n".join(userdata)

    c = get_connection()
    res = c.run_instances(ami, key_name=key_name, min_count=count,
                          max_count=count, security_groups=security_groups,
                          security_group_ids=security_group_ids,
                          user_data=userdata, subnet_id=subnet_id)

    time.sleep(1)  # sleep to decrease chances of instance ID does not exist
    for i in res.instances:
        i.add_tag('Name', name)
        i.add_tag('App', app)
        i.add_tag('Type', server_type)
        i.add_tag('Env', env)

    return res.instances
