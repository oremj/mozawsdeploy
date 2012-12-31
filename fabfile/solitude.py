from functools import partial

from fabric.api import task

from mozawsdeploy import ec2, rds


AMAZON_AMI = 'ami-2a31bf1a'

create_server = partial(ec2.create_server, app='solitude')


@task
def create_web(env, instance_type='m1.small'):
    """
    args: env, instance_type
    This function will create the "golden master" ami for solitude web servers.
    TODO: needs to user_data to puppetize server
    """
    create_server('web', server_type='web', env=env, ami=AMAZON_AMI,
                  security_groups=['solitude-base-%s' % env,
                                   'solitude-web-%s' % env])


@task
def create_rabbitmq(env, instance_type='m1.small'):
    """
    args: env, instance_type
    This function will create the "golden master" ami for solitude web servers.
    TODO: needs to user_data to puppetize server
    """
    create_server('rabbitmq', server_type='rabbitmq', env=env, ami=AMAZON_AMI,
                  security_groups=['solitude-base-%s' % env,
                                   'solitude-rabbitmq-%s' % env])


@task
def create_database(env, password, instance_type='db.m1.small'):
    """
    args: env, password, instance_type
    This function will create the master rw database for solitude.
    """
    rds_id = "solitude-%s-master" % env
    db_name = "solitude_%s" % env
    username = db_name
    create_rds(rds_id, db_name, username, password, server_type=instance_type,
                    param_group='solitude-mysql55',
                    security_groups=['solitude-%s-write' % env])
