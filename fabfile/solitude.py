from functools import partial

from fabric.api import task

from mozawsdeploy import ec2


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
def create_celery(env, instance_type='m1.small'):
    """
    args: env, instance_type
    This function will create the "golden master" ami for solitude web servers.
    TODO: needs to user_data to puppetize server
    """
    create_server('celery', server_type='celery', env=env, ami=AMAZON_AMI,
                  security_groups=['solitude-base-%s' % env,
                                   'solitude-celery-%s' % env])


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
