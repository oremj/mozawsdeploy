from boto.ec2 import connect_to_region


def create_server(name, app, server_type, env, ami,
                  security_groups, region='us-west-2', key_name=None):
    c = connect_to_region(region)
    res = c.run_instances(ami, key_name=key_name,
                          security_groups=security_groups)

    for i in res.instances:
        i.add_tag('Name', name)
        i.add_tag('App', app)
        i.add_tag('Type', server_type)
        i.add_tag('Env', env)

    return res.instances
