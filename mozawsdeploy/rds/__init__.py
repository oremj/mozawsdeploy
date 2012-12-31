import os
import sys

from boto.rds import connect_to_region

from .. import config


def get_connection():
    c = connect_to_region(config.region,
                          aws_access_key_id=config.aws_access_key_id,
                          aws_secret_access_key=config.aws_secret_access_key)

    return c


def create_rds(rds_id, db_name, username, password, engine='MySQL',
               allocated_storage='10', server_type='db.m1.small',
               multi_az=True, param_group=None, security_groups=None):
    c = get_connection()
    c.create_dbinstance(id=rds_id,
                        allocated_storage=allocated_storage,
                        instance_class=server_type,
                        engine=engine,
                        master_username=username,
                        master_password=password,
                        db_name=db_name,
                        param_group=param_group,
                        security_groups=security_groups,
                        multi_az=multi_az,
                        engine_version='5.5.27',
                        character_set_name='UTF-8',)


def create_replica(rds_id, master_rds_id, server_type='db.m1.small'):
    c = get_connection()
    try:
        if c.get_all_dbinstances(instance_id=master_rds_id):
            c.create_dbinstance_read_replica(id=rds_id,
                                             source_id=master_rds_id,
                                             instance_class=server_type,
                                             )
    except:
        print sys.exc_info()
