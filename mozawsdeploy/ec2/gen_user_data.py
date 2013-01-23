def init():
    return "\n".join(['#!/bin/bash',
                      'set -x',
                      'exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1'])


def yum_install(pkgs):
    return '/usr/bin/yum -y install %s' % ' '.join(pkgs)


def easy_install(pkg):
    return '/usr/bin/easy_install ' + pkg


def pyrepo_install(pkgs):
    return ('/usr/bin/pip install -U --no-index -f '
            'https://pyrepo.addons.mozilla.org/ %s' % ' '.join(pkgs))


def add_host(ip, host):
    return 'echo "%s %s" >> /etc/hosts' % (ip, host)


def run_puppet():
    return 'puppet agent --test --pluginsync --certname $(curl -s "http://169.254.169.254/latest/meta-data/instance-id")'
