def init():
    return '#!/bin/bash'


def yum_install(pkgs):
    return '/usr/bin/yum -y install %s' % ' '.join(pkgs)


def easy_install(pkg):
    return '/usr/bin/easy_install ' + pkg


def pyrepo_install(pkgs):
    return ('/usr/bin/pip install --no-index -f '
            'https://pyrepo.addons.mozilla.org/ %s' % ' '.join(pkgs))


def add_host(ip, host):
    return '%s %s >> /etc/hosts' % (ip, host)


def run_puppet():
    return 'puppet agent --test'
