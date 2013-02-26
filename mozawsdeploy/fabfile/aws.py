import time

from fabric.api import execute, output, settings, sudo, task
from mozawsdeploy import config, configure, ec2


configure()
AMAZON_AMI = config.amazon_ami


@task
def print_type(instance_type):
    output.status = False  # easier to use in bash scripts with this.
    instances = ec2.get_instances_by_tags({'Type': instance_type})
    for i in instances:
        print i.private_ip_address


@task
def print_instances():
    instances = ec2.get_vpc_instances()
    instances.sort(key=lambda x: x.tags.get('Type', ''))

    cur_type = None
    for instance in instances:
        inst_type = instance.tags.get('Type', 'No Type')
        if cur_type != inst_type:
            print inst_type
            cur_type = inst_type

        print "\t%s" % instance.private_ip_address


@task
def print_security_groups():
    c = ec2.get_connection()
    sgs = c.get_all_security_groups()
    sgs = [i for i in sgs if i.vpc_id == config.vpc_id]
    sgs.sort(key=lambda x: x.name)
    for sg in sgs:
        print "%s:" % sg.name
        for rule in sg.rules:
            if rule.to_port == rule.from_port:
                port = rule.from_port
            else:
                port = "%s-%s" % (rule.from_port,
                                  rule.to_port)

            if port is None:
                port = 'ALL'

            protocol = rule.ip_protocol
            if protocol == '-1':
                protocol = 'ALL'

            for grant in rule.grants:
                if grant.cidr_ip:
                    grant = grant.cidr_ip
                else:
                    grant = next(i for i in sgs
                                 if i.id == grant.group_id).name

                print "\t:%s/%s <- %s" % (port,
                                          protocol,
                                          grant)
        print


@task
def _run_puppet():
    sudo('puppetd -t')


@task
def run_puppet(instance_type='*'):
    """Runs puppetd -t all hosts specified by type"""
    instances = ec2.get_instances_by_tags({'Type': instance_type})
    with settings(hosts=[i.private_ip_address
                         for i in instances if i.private_ip_address]):
        execute(_run_puppet)


@task
def create_vpc_instance(server_type, subnet_id,
                        instance_type='m1.small', count=1):
    """Args: server_type, subnet_id, [instance_type, count]"""
    return create_server(server_type=server_type, subnet_id=subnet_id,
                         instance_type=instance_type, count=count)


def create_server(server_type, ami=AMAZON_AMI,
                  instance_type='m1.small', subnet_id=None, count=1):
    count = int(count)
    app = config.app
    env = config.env
    instances = ec2.create_server(name='%s.%s.%s' % (app, env, server_type),
                                  server_type=server_type,
                                  env=env, app=app, ami=ami,
                                  count=count, subnet_id=subnet_id,
                                  security_groups=['%s-base-%s' % (app, env),
                                                   '%s-%s-%s' % (app,
                                                                 server_type,
                                                                 env)])

    return instances


def wait_for_healthy_instances(lb_name, new_instance_ids, timeout):
    elb_conn = ec2.get_elb_connection()
    ec2_conn = ec2.get_connection()

    elb_conn.register_instances(lb_name, new_instance_ids)

    start_time = time.time()
    while True:
        if timeout < (time.time() - start_time):
            elb_conn.deregister_instances(lb_name, new_instance_ids)
            ec2_conn.create_tags(new_instance_ids, {'Status': 'FAILED'})
            raise Exception('Timeout exceeded.')

        instance_health = elb_conn.describe_instance_health(lb_name,
                                                            new_instance_ids)

        if all(i.state == 'InService' for i in instance_health):
            registered = elb_conn.describe_instance_health(lb_name)
            old_inst_ids = [i.instance_id for i in registered
                            if i.instance_id not in new_instance_ids]

            elb_conn.deregister_instances(lb_name, old_inst_ids)
            ec2_conn.create_tags(old_inst_ids, {'Status': 'OLD'})
            return

        time.sleep(10)


def deploy_instances_and_wait(create_instance, lb_name, ref,
                              count, wait_timeout):
    """create_instance must return a list of instances
       and take a ref and count"""
    instances = create_instance(release_id=ref, count=count)

    for i in instances:
        i.add_tag('Release', ref)

    new_inst_ids = [i.id for i in instances]

    print 'Sleeping for 2 min while instances build.'
    time.sleep(120)
    print 'Waiting for instances (timeout: %ds)' % wait_timeout
    wait_for_healthy_instances(lb_name, new_inst_ids, wait_timeout)
    print 'All instances healthy'
    print '%s is now running' % ref
