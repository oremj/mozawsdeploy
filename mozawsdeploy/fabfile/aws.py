import os
import re
import time
from functools import partial

from fabric.api import lcd, local, task

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
