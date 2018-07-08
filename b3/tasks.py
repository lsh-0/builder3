from invoke import task

@task
def moo(c):
    print(c)
    print('moo')
