import time
import re

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


def get_instances(instance_ids=None, filters=None):
    c = get_connection()
    res = c.get_all_instances(instance_ids=instance_ids, filters=filters)

    instances = []
    for r in res:
        instances += r.instances

    return instances


def prefix_instance_names(instance_ids, prefix):
    """Use this to add a tag to the beginning of the name
       for example prefix="FAILED." or prefix="OLD."
    """
    instances = get_instances(instance_ids)
    for i in instances:
        i.add_tag('Name', '%s%s' % (prefix, i.tags.get('Name', '')))


def get_vpc_instances():
    filters = {'vpc-id': config.vpc_id}
    return get_instances(filters=filters)


def get_instances_by_tags(tags):
    """tags should be a dict in the format {'tag': 'value'}"""
    filters = {'vpc-id': config.vpc_id}
    for tag, val in tags.iteritems():
        filters['tag:%s' % tag] = val

    return get_instances(filters=filters)


def get_instances_by_lb(lb_name):
    c = get_connection()
    elb_conn = get_elb_connection()

    instance_states = elb_conn.describe_instance_health(lb_name)

    return get_instances(instance_ids=[i.instance_id 
                                       for i in instance_states])


def get_security_group_ids(security_groups):
    c = get_connection()
    sg = c.get_all_security_groups(filters={'group-name': security_groups})
    return [i.id for i in sg if i.vpc_id == config.vpc_id]


class SecurityGroupInbound:
    def __init__(self, protocol, from_port, to_port, groups):
        self.protocol = protocol
        self.from_port = from_port
        self.to_port = to_port
        self.groups = groups


class SecurityGroup:
    def __init__(self, name, inbounds=None):
        self.name = name
        if inbounds:
            self.inbounds = inbounds
        else:
            self.inbounds = []


def create_security_policy(sec_policy, app, env):
    """sec_policy should be of the format:
           {'name': 'in': ['group1,group2:80/tcp']}"""

    security_groups = []
    for group, rules in sec_policy.iteritems():
        all_ingress = []
        for ingress in rules.get('in', []):
            groups, port = ingress.split(':')
            groups = groups.split(',')
            port, proto = port.split('/')
            all_ingress.append(SecurityGroupInbound(proto, port, port, groups))

        security_groups.append(SecurityGroup(group, all_ingress))

    create_security_groups(security_groups, app, env)
        


def create_security_groups(security_groups, app, env):
    c = get_connection()

    created_groups = {}
    cur_groups = [sg for sg in c.get_all_security_groups()
                  if sg.vpc_id == config.vpc_id]

    for sg in security_groups:
        full_sg = '%s-%s-%s' % (app, sg.name, env)
        desc = re.sub('-', ' ', full_sg)

        sec_group = None
        for i in cur_groups:  # Try to find the group
            if i.name == full_sg:
                sec_group = i
                break

        if sec_group is None:  # Create if it didn't exist
            sec_group = c.create_security_group(full_sg, desc, config.vpc_id)
            print 'Created: %s' % full_sg

        created_groups[sg.name] = sec_group

    for sg in security_groups:
        real_sg = created_groups[sg.name]
        for policy in sg.inbounds:
            for group in policy.groups:
                try:
                    try:
                        kwargs = {'src_group': created_groups[group]}
                    except KeyError:
                        kwargs = {'cidr_ip': group}

                    real_sg.authorize(ip_protocol=policy.protocol,
                                      from_port=policy.from_port,
                                      to_port=policy.to_port,
                                      **kwargs)

                    print 'Authorized: %s -> %s:%d/%s' % (group, sg.name,
                                                          policy.from_port,
                                                          policy.protocol)
                except Exception, e:
                    print e

    return created_groups


def get_instance(instance_ids=None, filters=None):
    """Returns the first instance returned by filters"""
    c = get_connection()
    reservations = c.get_all_instances(instance_ids=instance_ids,
                                       filters=filters)

    for r in reservations:
        for i in r.instances:
            return i


def create_server(name, app, server_type, env, ami,
                  security_groups=None, userdata=None,
                  count=1, key_name=None, subnet_id=None):

    if security_groups:
        security_group_ids = get_security_group_ids(security_groups)
    else:
        security_group_ids = None

    if not userdata:
        userdata = [gen_user_data.init(),
                    gen_user_data.yum_install(['puppet', 'git']),
                    gen_user_data.easy_install('pip'),
                    gen_user_data.pyrepo_install(['supervisor', 'virtualenv']),
                    gen_user_data.pyrepo_install(['supervisor', 'requests',
                                                  'app-packr', 'argparse',
                                                  'virtualenv']),
                    gen_user_data.add_host(config.puppet_ip, 'puppet'),
                    gen_user_data.set_hostname(name),
                    gen_user_data.run_puppet()]
        userdata = "\n".join(userdata)

    c = get_connection()
    res = c.run_instances(ami, key_name=key_name, min_count=count,
                          max_count=count,
                          security_group_ids=security_group_ids,
                          user_data=userdata, subnet_id=subnet_id)

    time.sleep(1)  # sleep to decrease chances of instance ID does not exist
    for i in res.instances:
        i.add_tag('Name', name)
        i.add_tag('App', app)
        i.add_tag('Type', server_type)
        i.add_tag('Env', env)

    return res.instances
