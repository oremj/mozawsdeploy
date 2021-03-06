def get_instance_id():
    return "$(curl -s 'http://169.254.169.254/latest/meta-data/instance-id')"


def init():
    return "\n".join(['#!/bin/bash',
                      'set -x',
                      'exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1'])


def yum_install(pkgs):
    return '/usr/bin/yum -y install %s' % ' '.join(pkgs)


def yum_clean():
    return '/usr/bin/yum clean all'


def yum_upgrade():
    return '/usr/bin/yum -y update --disablerepo=puppetlabs-*'


def easy_install(pkg):
    return '/usr/bin/easy_install ' + pkg


def pyrepo_install(pkgs):
    return ('/usr/bin/pip install --pre -U --no-index -f '
            'https://pyrepo.addons.mozilla.org/ %s' % ' '.join(pkgs))


def add_host(ip, host):
    return 'echo "%s %s" >> /etc/hosts' % (ip, host)


def set_hostname(type_, env, app):
    return 'hostname "%s.%s.%s.%s"' % (get_instance_id(), type_, env, app)


def run_puppet(puppet_host):
    return 'puppet agent --test --pluginsync --certname "%s" --server "%s"' % (get_instance_id(), puppet_host)


def reboot_host():
    return 'reboot'
