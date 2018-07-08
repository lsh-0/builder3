from invoke import task
from b3 import project, conf, terraform
import json

def pprint(d):
    print(json.dumps(d, indent=4))

@task
def pdata(c, pname):
    pprint(project.project_data(pname))

@task
def defaults(c, oname=None):
    defaults, _ = project.all_project_data(oname)
    pprint(defaults)

@task
def tform(c, pname):
    pprint(terraform.pdata_to_tform(project.project_data(pname)))
