import os

from boto.ec2 import connect_to_region

from . import gen_user_data
from . import config


def get_connection():
    c = connect_to_region(config.region,
                          aws_access_key_id=config.aws_access_key_id,
                          aws_secret_access_key=config.aws_secret_access_key)

    return c


def get_instance(filters):
    """Returns the first instance returned by filters"""
    c = get_connection()
    reservations = c.get_all_instances(filters=filters)

    for r in reservations:
        for i in r.instances:
            return i


def create_server(name, app, server_type, env, ami,
                  security_groups, userdata=None, key_name=None):

    if not userdata:
        userdata = [gen_user_data.init(),
                    gen_user_data.yum_install(['puppet', 'git']),
                    gen_user_data.easy_install('pip'),
                    gen_user_data.pyrepo_install(['supervisor', 'virtualenv']),
                    gen_user_data.add_host(config.puppet_ip, 'puppet'),
                    gen_user_data.run_puppet()]
        userdata = "\n".join(userdata)

    c = get_connection()
    res = c.run_instances(ami, key_name=key_name,
                          security_groups=security_groups, user_data=userdata)

    for i in res.instances:
        i.add_tag('Name', name)
        i.add_tag('App', app)
        i.add_tag('Type', server_type)
        i.add_tag('Env', env)

    return res.instances
