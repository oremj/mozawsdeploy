import yaml

from .ec2 import get_instance


def escape(word):
    return word.encode('ascii', 'ignore')


def create_node_yaml(fqdn):
    i = get_instance(instance_ids=[fqdn])
    if not i:
        return ''
    tclass = '%s_private::%s::%s' % (i.tags['App'],
                                     i.tags['Type'], i.tags['Env'])
    data = {'classes': [escape(tclass)]}
    data['parameters'] = {'ec2_app': escape(i.tags['App']),
                          'ec2_env': escape(i.tags['Env']),
                          'ec2_type': escape(i.tags['Type']),
                          'ec2_vpc': escape(i.vpc_id)}

    return yaml.dump(data, default_flow_style=False, indent=10)
