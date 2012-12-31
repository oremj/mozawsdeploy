import os

from boto.rds import connect_to_region

from .. import config


def get_connection():
    c = connect_to_region(config.region,
                          aws_access_key_id=config.aws_access_key_id,
                          aws_secret_access_key=config.aws_secret_access_key)

    return c


def create_rds(rds_id, db_name, username, password, engine='MySQL',
               allocate_storage='10', server_type='db.m1.small', multi_az=True,
               param_group=None, security_groups=None):
    c = get_connection()
    c.create_dbinstance(id=rds_id,
                        allocated_storage=allocate_storage,
                        instance_class=server_type,
                        engine=engine,
                        master_username=username,
                        master_password=password,
                        db_name=db_name,
                        param_group=param_group,
                        multi_az=multi_az,
                        engine_version='5.5.27',
                        character_set_name='UTF-8',)
