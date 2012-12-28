import yaml

from .ec2 import get_instance


def create_node_yaml(fqdn):
    i = get_instance(filters={'private_dns_name': fqdn})
    tclass = '%s::%s::%s' % (i.tags['App'], i.tags['Type'], i.tags['Env'])
    pclass = tclass.encode('ascii', 'ignore')
    data = {'classes': [pclass]}

    return yaml.dump(data, default_flow_style=False, indent=10)
