from boto.ec2 import connect_to_region


DEFAULT_REGION = 'us-west-2'


def get_instance(filters, region=DEFAULT_REGION):
    """Returns the first instance returned by filters"""
    c = connect_to_region(region)
    reservations = c.get_all_instances(filters=filters)

    for r in reservations:
        for i in r.instances:
            return i


def create_server(name, app, server_type, env, ami,
                  security_groups, region=DEFAULT_REGION, key_name=None):
    c = connect_to_region(region)
    res = c.run_instances(ami, key_name=key_name,
                          security_groups=security_groups)

    for i in res.instances:
        i.add_tag('Name', name)
        i.add_tag('App', app)
        i.add_tag('Type', server_type)
        i.add_tag('Env', env)

    return res.instances
