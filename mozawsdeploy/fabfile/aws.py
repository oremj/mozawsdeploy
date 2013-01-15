import time

from mozawsdeploy import ec2


AMAZON_AMI = 'ami-2a31bf1a'


def create_server(app, server_type, env, ami=AMAZON_AMI, instance_type='m1.small',
                  subnet_id=None, count=1):
    count = int(count)
    instances = ec2.create_server(server_type, server_type=server_type, env=env,
                                  app=app, ami=ami,
                                  count=count, subnet_id=subnet_id,
                                  security_groups=['%s-base-%s' % (app, env),
                                                   '%s-%s-%s' % (app, server_type,
                                                                 env)])

    return instances


def wait_for_healthy_instances(lb_name, new_instance_ids, timeout):
    elb_conn = ec2.get_elb_connection()

    elb_conn.register_instances(lb_name, new_instance_ids)

    start_time = time.time()
    while True:
        if timeout < (time.time() - start_time):
            elb_conn.deregister_instances(lb_name, new_instance_ids)
            raise Exception('Timeout exceeded.')

        instance_health = elb_conn.describe_instance_health(lb_name,
                                                            new_instance_ids)

        if all(i.state == 'InService' for i in instance_health):
            registered = elb_conn.describe_instance_health(lb_name)
            old_inst_ids = [i.instance_id for i in registered
                            if i.instance_id not in new_instance_ids]

            elb_conn.deregister_instances(lb_name, old_inst_ids)
            return

        time.sleep(10)
