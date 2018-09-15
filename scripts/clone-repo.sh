#!/bin/bash
# clones a repository to a project instance
# assumes cwd is the project instance directory (./project/instances/$iid/)
# run as the current user

set -eu

repo_name=$1
repo_url=$2

mkdir -p cloned-projects
cd cloned-projects

if [ ! -e "$repo_name" ]; then
    # repo doesn't exist, clone
    git clone "$repo_url" "$repo_name"
else
    # repo exists (or at least the dir does), try updating without 
    # destroying any local changes
    git pull || {
        echo "problem pulling changes for $repo_name"
    }
fi
