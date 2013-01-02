import os
import re
import time
from functools import partial

from fabric.api import lcd, local, task

from mozawsdeploy import ec2, rds


AMAZON_AMI = 'ami-2a31bf1a'

create_server = partial(ec2.create_server, app='solitude')


@task
def create_web(env, instance_type='m1.small', count=1):
    """
    args: env, instance_type
    This function will create the "golden master" ami for solitude web servers.
    """

    count = int(count)
    instances = create_server('web', server_type='web', env=env,
                              ami=AMAZON_AMI, count=count,
                              security_groups=['solitude-base-%s' % env,
                                               'solitude-web-%s' % env])

    elb_conn = ec2.get_elb_connection()
    elb_conn.register_instances('solitude-%s' % env, [i.id for i in instances])


@task create_syslog(env, instance_type='m1.small'):
    """
    args: env, instance_type
    """
    instances = create_server('syslog', server_type='syslog', env=env,
                              ami=AMAZON_AMI,
                              security_groups=['solitude-base-%s' % env,
                                               'solitude-syslog-%s' % env])


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


@task
def create_database(env, password, instance_type='db.m1.small'):
    """
    args: env, password, instance_type
    This function will create the master rw database for solitude.
    """
    rds_id = "solitude-master-%s" % env
    db_name = "solitude_%s" % env
    username = db_name
    rds.create_rds(rds_id, db_name, username, password,
                   server_type=instance_type, param_group='solitude-mysql55',
                   security_groups=['solitude-db-write-%s' % env])


@task
def create_database_replica(env, instance_type='db.m1.small'):
    """
    args: env, instance_type
    This function will create the replica ro database for solitude.
    """
    rds_id = "solitude-replica-%s" % env
    master_rds_id = "solitude-master-%s" % env
    rds.create_replica(rds_id, master_rds_id, server_type=instance_type)


@task
def build_release(project_dir, ref):
    """Build release. This assumes puppet has placed settings in /settings"""
    release_time = time.time()
    release_dir = os.path.join(project_dir, 'solitude-%d-%s' %
                               (release_time,
                                re.sub('[^A-z0-9]', '.', ref)))

    local('mkdir %s' % release_dir)
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

    local('cp %s/settings/local.py %s/solitude/solitude/settings/local.py' %
          (project_dir, release_dir))

    with lcd(project_dir):
        local('ln -snf %s/solitude solitude' % release_dir)
        local('ln -snf %s/venv venv' % release_dir)

