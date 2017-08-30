from fabric.api import run, local

def hello_world():
    print('hello world')

def create_tarball(include_help = False):
    # copy the 
    local('cp streetview/settings-dove.py streetview/settings.py', capture=False)
    if include_help:
        local('tar czf /tmp/streetview.tgz streetview/', capture=False)
    else:
        local('tar --exclude="static/help/*" -czf /tmp/streetview.tgz streetview/', capture=False)
    local('cp streetview/settings-local.py streetview/settings.py', capture=False)

def copy_tarball():
    local('scp /tmp/streetview.tgz sjm2186@dove.iserp.columbia.edu:~/streetview/streetview.tgz')

def unpack_remote_tarball():
    local('ssh sjm2186@dove.iserp.columbia.edu tar xvzf streetview/streetview.tgz -C /home/sjm2186/streetview')

def create_canvasplatform_tarball(include_help = False):
    # copy the 
    local('cp streetview/settings-canvasplatform.py streetview/settings.py', capture=False)
    if include_help:
        local('tar czf /tmp/streetview.tgz streetview/', capture=False)
    else:
        local('tar --exclude="static/help/*" -czf /tmp/streetview.tgz streetview/', capture=False)
    local('cp streetview/settings-local.py streetview/settings.py', capture=False)

def copy_canvasplatform_tarball():
    local('scp /tmp/streetview.tgz canvasuser@184.106.30.25:httpdocs/streetview.tgz')

def unpack_canvasplatform_tarball():
    local('ssh canvasuser@184.106.30.25 tar xvzf httpdocs/streetview.tgz -C httpdocs')


def create_webfaction_tarball(include_help = False):
    # copy the 
    local('cp streetview/settings-webfaction.py streetview/settings.py', capture=False)
    if include_help:
        local('tar czf /tmp/streetview.tgz streetview/', capture=False)
    else:
        local('tar --exclude="static/help/*" -czf /tmp/streetview.tgz streetview/', capture=False)
    local('cp streetview/settings-local.py streetview/settings.py', capture=False)

def copy_webfaction_tarball():
    local('scp /tmp/streetview.tgz canvasplat@web524.webfaction.com:~/webapps/django/streetview.tgz')

def unpack_webfaction_tarball():
    local('ssh canvasplat@web524.webfaction.com tar xvzf webapps/django/streetview.tgz -C webapps/django/')

def create_webfaction_dove_tarball(include_help = False):
    # copy the 
    local('cp streetview/settings-webfaction-dove.py streetview/settings.py', capture=False)
    if include_help:
        local('tar czf /tmp/streetview.tgz streetview/', capture=False)
    else:
        local('tar --exclude="static/help/*" -czf /tmp/streetview.tgz streetview/', capture=False)
    local('cp streetview/settings-local.py streetview/settings.py', capture=False)

def copy_webfaction_dove_tarball():
    local('scp /tmp/streetview.tgz canvasplat@web524.webfaction.com:~/webapps/dove/streetview.tgz')

def unpack_webfaction_dove_tarball():
    local('ssh canvasplat@web524.webfaction.com tar xvzf webapps/dove/streetview.tgz -C webapps/dove/')



def reload_apache():
    local('ssh sjm2186@dove.iserp.columbia.edu sudo /etc/init.d/apache2 reload')

def run_tests():
    local('python streetview/manage.py test ratestreets', capture=False)

def deploy():
    create_tarball()
    copy_tarball()
    unpack_remote_tarball()

def canvasplatform():
    create_canvasplatform_tarball()
    copy_canvasplatform_tarball()
    unpack_canvasplatform_tarball()

def webfaction():
    create_webfaction_tarball()
    copy_webfaction_tarball()
    unpack_webfaction_tarball()

def webfaction_dove():
    create_webfaction_dove_tarball()
    copy_webfaction_dove_tarball()
    unpack_webfaction_dove_tarball()

def deploy_help():
    create_tarball(True)
    copy_tarball()
    unpack_remote_tarball()

def host_type():
    run('uname -s')
