# builder, attempt #3

A program for describing infrastructure requirements for multiple projects.

## project definitions

Project definitions live in the `b3.conf.PROJECT_DIR` directory.

The `default.yaml` set of project definitions is used by this project.

### project resources

A project definition is a list or mapping of 'resources' and configuration 
variables that will be used to create terraform templates.

A 'resource' is simply a block of configuration describing a 'thing': a VPC, an
S3 bucket, an EC2 instance, etc.

### project instances

After describing your project (a list of resources), you then create a new 
*instance* of that project:

    ./bldr new:project-name,instance-name
    
The files for this project instance will live in `./project/instances` as
`project-name--instance-name`. This is the "instance ID" or **iid** and is used 
to refer to this instance thereafter.

If an instance exists, you will be prompted to *update* that instance:

    ./bldr update:iid

This will re-render any templates or configuration but not change deployed 
resources.

## Provisioning

Provisioning just means preparing and creating infrastructure so that a project
can be configured upon it.

Depending on the type of infrastructure, 

### Terraform

Terraform is used to provision certain project resources. These include:

* ec2
* ec2 security groups
* vpc

### Vagrant

Vagrant is used to provision the 'vagrant' resource.

### remote and local actual machines

What if a project is not running on virtual infrastructure, like a virtualbox or 
remote ec2 vm?

In that case, there is no infrastructure to provision leaving just configuration.

## Configuring

After the infrastructure has been provisioned (or not, in some cases), it needs
to be configured.

Virtual machines often require the *most* configuration, installing many pieces 
of software with specific configuration. There may also be infrastructure that 
requires configuring into a certain state that Terraform couldn't accomplish
during provisioning.

And there may be multiple instances of resources that all require different 
configuration, like N ec2 instances, or N ec2 instances and an s3 bucket that 
needs an object present. All need configuring in a consistent fashion.

The purpose of Builder is to find the best and shortest path to go from 
Nothing to your Final Configured State.

### virtual machines, actual machines and bootstrap

In the context of Builder, 'bootstrapping' a machine is bringing it into a 
specific state so that it can be connected to and the software used for 
automating configuration be installed on it.

Both Vagrant and Terraform have hooks that allow commands to be executed on the 
guest directly after provisioning. In the case of actual machines, scripts are 
executed directly by Python+Fabric.

In all cases the script `./scripts/bootstrap.sh` is run in order to install and
configure Salt, the software that will automate the installation and 
configuration of software.

### other infrastructure

Is completely unsupported but also completely reasonable.

After creating/updating non-vm infrastructure, may we not want to run a script
or some code and have access to the project and resource data?



