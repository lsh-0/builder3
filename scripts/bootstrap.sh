#!/bin/bash
# Ansible requires hosts to have python installed
# We don't want to connect as root if we can avoid it
# run as ROOT

set -eu # everything must pass, no unbound variables

deploy_user_name=$1 # name of user to be created with permissions to execute ansible states

# if user doesn't exist, create, grant root perms
id --user "$deploy_user_name" > /dev/null || {
    echo "creating $deploy_user_name"
    useradd \
        --create-home \
        --shell /bin/bash \
        "$deploy_user_name"

    # for gui login
    # password login via ssh is disabled
    password="password" # obviously it will be changed
    echo "$deploy_user_name:$password" | chpasswd

    sudoers_entry="Defaults:$deploy_user_name !requiretty\n$deploy_user_name ALL=(ALL) NOPASSWD: ALL"
    printf "$sudoers_entry" > "/etc/sudoers.d/$deploy_user_name"
}

test -f /root/bootstrap-pull.flag || {
    echo "updating packages"
    pacman -Sy
    touch /root/bootstrap-pull.flag
}

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

test -f /root/bootstrap-python.flag || {
    echo "installing python"
    pacman -S python --noconfirm
    touch /root/bootstrap-python.flag
}

test ! -f /root/.ssh/authorized_keys || {
    # WARN: big assumption here
    # it's assumed the root user is being accessed via a pubkey and not a password
    # this is intended as a once-off. if the deploy user's authorized keys do
    # get mangled, it's assumed configuration will fix it or it wasn't important
    echo "moving root's authorized_keys to $deploy_user_name's authorized_keys"
    mkdir -p "/home/$deploy_user_name/.ssh/"
    cp /root/.ssh/authorized_keys "/home/$deploy_user_name/.ssh/authorized_keys"
    chmod 700 "/home/$deploy_user_name/.ssh"
    chmod 600 "/home/$deploy_user_name/.ssh/authorized_keys"
    chown "$deploy_user_name":"$deploy_user_name" -R "/home/$deploy_user_name/.ssh"
}
    

printf "\n   ◕ ‿‿ ◕   all done\n "

