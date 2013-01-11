import os
import re
import time
from functools import partial

from fabric.api import lcd, local, task

from mozawsdeploy import config, ec2
from mozawsdeploy.fabfile import aws


AMAZON_AMI = 'ami-2a31bf1a'
SUBNET_ID = config.subnet_id

create_server = partial(aws.create_server, app='solitude', ami=AMAZON_AMI,
                        subnet_id=SUBNET_ID)


@task
def create_web(env, instance_type='m1.small', count=1):
    """
    args: env, instance_type
    This function will create the "golden master" ami for solitude web servers.
    """

    instances = create_server(server_type='web', env=env, instance_type=instance_type,
                              count=count)

    elb_conn = ec2.get_elb_connection()
    elb_conn.register_instances('solitude-%s' % env, [i.id for i in instances])


@task
def create_syslog(env, instance_type='m1.small'):
    """
    args: env, instance_type
    """
    instances = create_server(server_type='syslog', env=env,
                              instance_type=instance_type)


@task
def create_celery(env, instance_type='m1.small'):
    """
    args: env, instance_type
    This function will create the "golden master" ami for solitude web servers.
    TODO: needs to user_data to puppetize server
    """
    instances = create_server(server_type='celery', env=env,
                              instance_type=instance_type)


@task
def create_sentry(env, instance_type='m1.small'):
    """
    args: env, instance_type
    This function will create the "golden master" ami for solitude web servers.
    TODO: needs to user_data to puppetize server
    """
    instances = create_server(server_type='sentry', env=env,
                              instance_type=instance_type)


@task
def create_rabbitmq(env, instance_type='m1.small'):
    """
    args: env, instance_type
    This function will create the "golden master" ami for solitude web servers.
    TODO: needs to user_data to puppetize server
    """
    instances = create_server(server_type='rabbitmq', env=env,
                              instance_type=instance_type)


@task
def create_graphite(env, instance_type='m1.small'):
    """
    args: env, instance_type
    This function will create the "golden master" ami for solitude web servers.
    TODO: needs to user_data to puppetize server
    """
    instances = create_server(server_type='graphite', env=env,
                              instance_type=instance_type)


@task
def create_security_groups(env):
    """
    args: env
    This function will create security groups for the specified env
    """
    security_groups = ['solitude-base-%s' % env,
                       'solitude-celery-%s' % env,
                       'solitude-graphite-%s' % env,
                       'solitude-graphite-elb-%s' % env,
                       'solitude-rabbitmq-%s' % env,
                       'solitude-rabbitmq-elb-%s' % env,
                       'solitude-sentry-%s' % env,
                       'solitude-sentry-elb-%s' % env,
                       'solitude-syslog-%s' % env,
                       'solitude-web-%s' % env,
                       'solitude-web-elb-%s' % env]

    ec2.create_security_groups(security_groups)


def build_release(project_dir, ref):
    """Build release. This assumes puppet has placed settings in /settings"""
    release_time = time.time()
    release_id = 'solitude-%d-%s' % (release_time, re.sub('[^A-z0-9]',
                                                          '.', ref))
    release_dir = os.path.join(project_dir, 'builds', release_id)
    tarball = os.path.join(project_dir, 'releases', '%s.tar.gz' % release_id)

    local('mkdir -p %s' % release_dir)
    local('git clone git://github.com/mozilla/solitude.git %s/solitude'
          % release_dir)
    with lcd('%s/solitude' % release_dir):
        local('git reset --hard %s' % ref)

    local('virtualenv --distribute --never-download %s/venv' % release_dir)
    local('%s/venv/bin/pip install --exists-action=w --no-deps '
          '--no-index --download-cache=/tmp/pip-cache '
          '-f https://pyrepo.addons.mozilla.org '
          '-r %s/solitude/requirements/prod.txt' %
          (release_dir, release_dir))
    local('rm -f %s/venv/lib/python2.6/no-global-site-packages.txt' %
          release_dir)
    local('%s/venv/bin/python /usr/bin/virtualenv --relocatable %s/venv' %
          (release_dir, release_dir))

    local('rsync -av %s/settings/ %s/solitude/solitude/settings/' %
          (project_dir, release_dir))

    local('rsync -av %s/aeskeys/ %s/aeskeys/' % (project_dir, release_dir))

    local('tar czf %s -C %s solitude aeskeys venv' %
          (tarball, release_dir))

    with lcd(project_dir):
        local('ln -snf %s/solitude solitude' % release_dir)
        local('ln -snf %s/venv venv' % release_dir)
        local('ln -snf %s latest.tar.gz' % tarball)
