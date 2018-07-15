import os, sys
from os.path import join
from invoke import task
from b3 import project, conf, context, terraform
import json
from pygments import highlight
from pygments import lexers
from pygments import formatters
from functools import wraps

def cpprint(d):
    "colourised pretty printer"
    data = json.dumps(d, indent=4)
    lexer = lexers.Python3Lexer()
    formatter = formatters.TerminalFormatter()
    sys.stdout.write((highlight(data, lexer, formatter)))

# not working with @task atm
# https://github.com/pyinvoke/invoke/issues/555
def buserr(fn):
    @wraps(fn)
    def wrapper(c, *args, **kwargs):
        try:
            return cpprint(fn(c, *args, **kwargs))
        except AssertionError as err:
            print(err)
    return wrapper

@task
@buserr
def foobar(c, p1):
    print(p1)
    raise AssertionError('baz')

#
#
#

@task
def pdata(c, pname):
    cpprint(project.project_data(pname))

@task
def defaults(c, oname=None):
    defaults, _ = project.all_project_data(oname)
    cpprint(defaults)

def pick_project():
    return 'p1'

def pick_iname():
    return 'foo'

@task
def new(c, pname=None, iname=None):
    pname = pname or pick_project()
    iname = iname or pick_iname()
    ctx = context.build(pname, iname)
    template = terraform.pdata_to_tform(project.project_data(pname), ctx)
    cpprint(template)
    path = terraform.write_template(ctx['iid'], template)
    print("wrote", path)
