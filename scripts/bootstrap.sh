#!/bin/bash
# Ansible requires hosts to have python installed
# We don't want to connect as root if we can avoid it
# run as ROOT

set -eux # everything must pass, no unbound variables

pname=$1 # ll 'myprojectname'
iname=$2 # ll 'prod' or 'end2end' or 'vagrant'
os=$3 # name of distro, used for switching between specific commands
deploy_user_name=$4 # name of user to be created with permissions to execute ansible states

iid="$pname--$iname"

vagrant=false
if [ -d /vagrant ]; then vagrant=true; fi

masterless=true

# who knows what state arch is in or how old it is
# don't proceed until we're running latest

echo "updating system"
if [ "$os" == "arch" ]; then
    pacman -Syu --noconfirm
else
    apt-get update -y
fi

# if user doesn't exist, create, grant root perms
id --user "$deploy_user_name" > /dev/null || {
    echo "creating $deploy_user_name"
    useradd \
        --create-home \
        --shell /bin/bash \
        "$deploy_user_name"
}

test -f /root/deploy-user-password-set.flag || {
    echo "setting deploy user password"
    # for gui login, password login via ssh is disabled
    password="password" # obviously it will be changed
    echo "$deploy_user_name:$password" | chpasswd
    touch /root/deploy-user-password-set.flag
}

test -f "/etc/sudoers.d/$deploy_user_name" || {
    echo "granting sudo"
    sudoers_entry="Defaults:$deploy_user_name !requiretty\n$deploy_user_name ALL=(ALL) NOPASSWD: ALL"
    printf "$sudoers_entry" > "/etc/sudoers.d/$deploy_user_name"
}

test -d "/home/$deploy_user_name/.ssh" || {
    echo "configuring ssh"
    if $vagrant; then
        # if vagrant, we can't re-use the insecure-by-default keypair belonging to the vagrant user
        # create a new set for the deploy user and ensure we have a copy to login with in the future
        sudo --user "$deploy_user_name" sh -c "
            set -e
            ssh-keygen -t rsa -f /home/$deploy_user_name/.ssh/id_rsa -N ''
            cd /home/$deploy_user_name/.ssh
            cat id_rsa.pub > authorized_keys
            chmod 600 authorized_keys"
        mkdir -p "/vagrant/project/instances/$iid/"
        cp -R "/home/$deploy_user_name/.ssh" "/vagrant/project/instances/$iid/"
    fi
    # if ec2, the deploy user shares the keypair generated for the bootstrap user
}

if [ "$os" == "arch" ]; then
    test -f /root/bootstrap-nm.flag || {
        echo "installing NetworkManager"
        pacman -S networkmanager dhcpcd --noconfirm
        systemctl disable netctl
        systemctl stop netctl
        
        systemctl enable NetworkManager
        systemctl start NetworkManager
        
        sleep 3 # urgh
        ping -c 3 duckduckgo.net

        touch /root/bootstrap-nm.flag
    }
fi

test -f /root/bootstrap-salt.flag || {
    if [ "$os" == "arch" ]; then
        echo "installing Salt"
        pacman -S salt --noconfirm
    else
        wget -O salt_bootstrap.sh https://bootstrap.saltstack.com --no-verbose
        # -P  Allow pip based installations.
        # -F  Allow copied files to overwrite existing(config, init.d, etc)
        # -c  Temporary configuration directory
        # https://github.com/saltstack/salt-bootstrap/blob/develop/bootstrap-salt.sh
        sh salt_bootstrap.sh -P -F -c /tmp stable 2018.3
    fi
    touch /root/bootstrap-salt.flag
}

if $masterless; then
    test -f /root/bootstrap-salt-config.flag || {
        echo "configuring Salt (masterless)"
        systemctl disable salt-minion || echo "salt-minion disabled"
        systemctl stop salt-minion || echo "salt-minion stopped"
        rm -rf /etc/salt/master
        mkdir -p /salt
        echo "$iid" > /etc/salt/minion_id
        echo "file_client: local # masterless
file_roots:
  base:
    - /salt
pillar_roots:
  base:
    - /salt/pillar
    " > /etc/salt/minion

        {
            cd /salt
            ln -sf example.top top.sls
        }
    }
fi



# TODO: this section needs more thought
# the below is essentially "if 'actual', checkout my home formula and hook it up"
# it needs to be, "if not 'vagrant', checkout *project formula* and hook it up"
if ! $vagrant; then
    # if vagrant, the local 'common' formula will be mounted at /salt
    # if run locally, we need symlinks to that formula
    formula_dir="/home/$deploy_user_name/dev/scripts/salt-vagrant-arch/salt"
    if [ ! -d "$formula_dir" ]; then
        mkdir -p "/home/$deploy_user_name/dev/scripts/"
        (
            cd /home/$deploy_user_name/dev/scripts
            pacman -S git --noconfirm
            git clone git@bitbucket.org:lskibinski/salt-vagrant-arch
        )
    fi
    
    if [ -d "$formula_dir" ]; then
        {
            cd /salt
            rm -f top.sls common pillar # symlinks
            # create new
            ln -sf "$formula_dir/top.sls"
            ln -sf "$formula_dir/common"
            ln -sf "$formula_dir/pillar"
        }
    fi
fi

printf "\n   ◕ ‿‿ ◕   all done\n "

