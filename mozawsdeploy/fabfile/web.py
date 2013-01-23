import os
import re
import time

from fabric.api import local, lcd


def create_virtualenv(release_dir):
    local('virtualenv --distribute --never-download %s/venv' % release_dir)


def pip_install(release_dir, requirements):
    local('%s/venv/bin/pip install --exists-action=w --no-deps '
          '--no-index --download-cache=/tmp/pip-cache '
          '-f https://pyrepo.addons.mozilla.org '
          '-r %s' %
          (release_dir, requirements))


def relocatable_virtualenv(release_dir):
    local('%s/venv/bin/python /usr/bin/virtualenv --relocatable %s/venv' %
          (release_dir, release_dir))


def install_requirements(release_dir, requirements):
    create_virtualenv(release_dir)
    pip_install(release_dir, requirements)
    local('rm -f %s/venv/lib/python2.6/no-global-site-packages.txt' %
          release_dir)
    relocatable_virtualenv(release_dir)


def build_release(app, project_dir, repo, ref, requirements, settings_dir,
                  release_id=None, build_dir=None, extra=None):
    """Build release. This assumes puppet has placed settings in /settings
       requirements and settings_dir are relative to release_dir
       If extra is defined, it will be a function that takes "release_dir"
       as an arg. it is executed right before symlinking the release.

       Returns: release_id
    """
    if not release_id:
        release_time = time.time()
        release_id = ('%d-%s' % (release_time, re.sub('[^A-z0-9]',
                                                      '.', ref)))[:21]

    if build_dir:
        release_dir = os.path.join(build_dir, release_id)
    else:
        release_dir = os.path.join(project_dir, 'builds', release_id)

    app_dir = os.path.join(release_dir, app)
    requirements = os.path.join(app_dir, requirements)
    settings_dir = os.path.join(app_dir, settings_dir)

    local('mkdir -p %s' % release_dir)
    local('git clone %s %s' % (repo, app_dir))
    with lcd(app_dir):
        local('git reset --hard %s' % ref)

    install_requirements(release_dir, requirements)

    local('rsync -av %s/settings/ %s/' % (project_dir, settings_dir))

    if extra:
        extra(release_dir)

    return release_id
