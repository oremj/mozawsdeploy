import os
import re
import shutil
import time
from datetime import datetime

from fabric.api import local, lcd


def build_release(app, project_dir, repo, ref, requirements, settings_dir,
                  extra=None):
    """Build release. This assumes puppet has placed settings in /settings
       requirements and settings_dir are relative to release_dir
       If extra is defined, it will be a function that takes "release_dir"
       as an arg. it is executed right before symlinking the release.

       Returns: release_id
    """
    release_time = time.time()
    release_id = '%s-%d-%s' % (app, release_time, re.sub('[^A-z0-9]',
                                                         '.', ref))
    release_dir = os.path.join(project_dir, 'builds', release_id)

    requirements = os.path.join(release_dir, app, requirements)
    settings_dir = os.path.join(release_dir, app, settings_dir)

    local('mkdir -p %s' % release_dir)
    local('git clone %s %s/%s' % (repo, release_dir, app))
    with lcd('%s/%s' % (release_dir, app)):
        local('git reset --hard %s' % ref)

    local('virtualenv --distribute --never-download %s/venv' % release_dir)
    local('%s/venv/bin/pip install --exists-action=w --no-deps '
          '--no-index --download-cache=/tmp/pip-cache '
          '-f https://pyrepo.addons.mozilla.org '
          '-r %s' %
          (release_dir, requirements))
    local('rm -f %s/venv/lib/python2.6/no-global-site-packages.txt' %
          release_dir)
    local('%s/venv/bin/python /usr/bin/virtualenv --relocatable %s/venv' %
          (release_dir, release_dir))

    local('rsync -av %s/settings/ %s/' % (project_dir, settings_dir))

    if extra:
        extra(release_dir)

    with lcd(project_dir):
        local('ln -snf %s/%s %s' % (release_dir, app, app))
        local('ln -snf %s/venv venv' % release_dir)

    return release_id


def remove_old_releases(project_dir, keep=4):
    """args: keep (default 4) must be at least 2"""

    assert keep >= 2

    build_dir = os.path.join(project_dir, 'builds')

    builds = []
    for d in os.listdir(build_dir):
        app, timestamp, ref = d.split('-')
        dt = datetime.fromtimestamp(int(timestamp))
        builds.append((dt, os.path.join(build_dir, d)))

    removed = 0
    builds.sort()
    for b, d in builds[:-keep]:
        shutil.rmtree(d)
        removed += 1

    print "Removed %d old releases." % removed


