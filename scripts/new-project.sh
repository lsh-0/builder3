#!/bin/bash

set -e  # everything must pass
set -u  # no unbound variables
set -x # show interpolation

appname=$1

mkdir -p cloned-projects
cd ./cloned-projects

# rough check formula doesn't already exist
if [ -d "$appname-formula" ]; then
    echo "directory $appname-formula already exists. quitting"
    exit 1
fi

# create/update example project
example_project="builder3-example-project"
if [ ! -e "$example_project" ]; then
    git clone https://bitbucket.org/lskibinski/builder3-example-project "$example_project"
else
    (
        cd "$example_project"
        git reset --hard
        git pull
    )
fi

cp -R "$example_project" "$appname-formula"
cd "$appname-formula"

rm -rf .git
rm README.md
rm salt/README.md
rm -rf salt/example-project
rm salt/pillar/example-project.sls

cp .README.template README.md
rm .README.template

(
    # jump into the formula's 'salt' root as a subshell (else shell lint cries)
    cd salt || exit

    # create an empty state file
    mkdir "$appname"
    #touch "$appname/init.sls"
    echo "echo 'hello, world':
    cmd.run" > "$appname/init.sls"

    # generate an example top salt file
    echo "base:
    '*':
        - $appname" > ./example.top

    # replace the example.pillar file with a generated+empty one
    echo "$appname:
    no: data" > "./pillar/$appname.sls"

    # generate an example top pillar file
    echo "base:
    '*':
        - $appname" > ./pillar/top.sls
)

# render the readme template
sed -i "s/\$appname/$appname/g" README.md

# init the repo
git init
git add .
git commit -am "initial commit"

