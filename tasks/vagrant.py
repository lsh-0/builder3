from os.path import join
from b3 import project, utils, conf
from b3.utils import repo_name

# vagrant wrangling
# TODO: shift this to b3/vagrant.py

def clone_repos(pname):
    pdata = project.project_data(pname)
    cfg = project.get_resource(pdata, 'project-config')
    # order isn't important
    repo_list = [cfg['private-formula-url'], cfg['project-formula-url']] + cfg['formula-dependencies']
    return utils.lmap(utils.clone_repo, repo_list)

def gen_etc_salt_minion(pname):
    "generates a /etc/salt/minion conf file for masterless Salt instances"
    pdata = project.project_data(pname)
    cfg = project.get_resource(pdata, 'project-config')
    
    # stock standard conf struct for any project with a formula
    # /salt is a shared directory, it points to ./cloned-projects/formula-name/salt
    etc_salt_minion = {
        'file_client': 'local', # don't talk to master
        'log_level': 'info', # emit what highstate is up to instead of going completely silent
        'file_roots': {
            'base': [],
        },
        'pillar_roots': {
            'base': []
        }
    }
    
    # add formula dependencies
    # order is very important (and very confusing).

    # the actual pillar files themselves, not their content, are subject to the order specified in pillar_roots
    # in this example:
    # pillar_roots:
    #   base:
    #     - /foo/pillar
    #     - /bar/pillar
    # a pillar file `/foo/pillar/pants.sls` will be used over `/bar/pillar/pants.sls` and bar's content is ignored
    # this is the 'first-found' strategy: https://docs.saltstack.com/en/latest/ref/file_server/file_roots.html#directory-overlay

    # to alter the pillar structure introduced by `/foo/pillar/pants.sls`, the pillar
    # file `/bar/pillar/party.sls` may selectively re-define parts and then Salt will merge those in 'over the top'.
    # this is the 'merge-last' strategy: https://docs.saltstack.com/en/latest/ref/pillar/all/salt.pillar.stack.html#merging-strategies

    # the same applies to salt states/file_roots. they are ultimately just a YAML struct too.
    
    # thus, for the *_roots, we want this order:
    #   private, project, dependent
    # this allows for private data to gazump everything (if present) and project data to override dependencies

    repo_list = [cfg['private-formula-url'], cfg['project-formula-url']] + cfg['formula-dependencies']
    file_roots = ['/salt/%s/salt' % repo_name(repo) for repo in repo_list]
    pillar_roots = ['/salt/%s/salt/pillar' % repo_name(repo) for repo in repo_list]
    
    etc_salt_minion['file_roots']['base'] = file_roots
    etc_salt_minion['pillar_roots']['base'] = pillar_roots

    return etc_salt_minion

def write_etc_salt_minion(pname):
    """writes the results of `gen_etc_salt_minion` to `$formula-clone/salt/etc-salt-minion`. 
    bootstrap will use this file on masterless instances if found"""
    pdata = project.project_data(pname)
    formula_name = repo_name(project.get_resource(pdata, 'project-config')['project-formula-url'])
    etc_salt_minion = gen_etc_salt_minion(pname)
    utils.dump_yaml(etc_salt_minion, join(conf.CLONED_PROJECT_DIR, formula_name, 'salt', 'etc-salt-minion'))
    return etc_salt_minion
