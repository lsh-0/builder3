# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANT_COMMAND = ARGV[0]

DEPLOY_USER=ENV["BLDR_DEPLOY_USER"] # "luke"
PNAME=ENV["BLDR_PNAME"] # "home"
INAME=ENV["BLDR_INAME"] # "desktop"
IID=ENV["BLDR_IID"] # "home--desktop"
BOX=ENV["BLDR_VAGRANT_BOX"]
REPO_NAME=ENV["BLDR_PROJECT_REPO"] # "home-formula" but also "asfasdfsad"

PROJECT_PATH="project/instances/#{IID}"

CUSTOM_SSH_KEY = File.expand_path("#{PROJECT_PATH}/#{IID}_rsa") # pem
CUSTOM_SSH = File.exists?(CUSTOM_SSH_KEY)
CUSTOM_SSH_USERNAME = DEPLOY_USER

if BOX.include? "ubuntu"
    OS="ubuntu"
else
    OS="arch"
end

def runcmd(cmd)
    output = nil
    IO.popen(cmd) do |io|
        output = io.read
    end
    exit_status = $?.exitstatus
    if exit_status != 0 
      throw "Command '#{cmd}' exited with #{exit_status}"
    end
    return output
end


# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
    config.vm.box = BOX
    config.vm.box_check_update = false
    config.ssh.insert_key = false

    # "./project/instances/pname--iname/cloned-projects/pname-formula/salt"
    config.vm.synced_folder "./cloned-projects/#{REPO_NAME}/salt/", "/salt"

    print [PNAME, INAME, DEPLOY_USER]

    config.vm.define IID do |project|
        project.vm.provision("shell", path: "scripts/bootstrap.sh", \
            keep_color: true, privileged: true, args: [PNAME, INAME, OS, DEPLOY_USER])
    end

    if CUSTOM_SSH and ["ssh", "ssh-config"].include? VAGRANT_COMMAND
        # ssh in as the DEPLOY user
        # a keypair should have been generated during bootstrap
        config.ssh.username = CUSTOM_SSH_USERNAME
        config.ssh.private_key_path = CUSTOM_SSH_KEY
    end
    
end
