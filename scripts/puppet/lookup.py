import sys

import yaml

from mozawsdeploy.puppet import create_node_yaml

fqdn = sys.argv[1]

print create_node_yaml(fqdn)