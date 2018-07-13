from . import utils

def thread(d, *tform_list):
    d = utils.deepcopy(d) # don't modify what we were given
    for fn in tform_list:
        d = fn(d)
    return d

def dictfilterv(fn, d):
    "filters given dict where fn(val) is truthy"
    return {key: val for key, val in d.items() if fn(val)}

def dictmap(fn, d):
    "maps given fn to fn(key, val)"
    return [fn(key, val) for key, val in d.items()]

#
#
#

def ec2(pdata):
    def _ec2(rname, rdata):
        aws_instance = {
            "ami": rdata['image']['id'],
            "instance_type": rdata['size'],
        }
        return {'aws_instance': [{rname: aws_instance}]}
    vms = dictfilterv(lambda v: v['type'] == 'vm', pdata)
    return dictmap(_ec2, vms)

def vpc(pdata):
    return []

def pdata_to_tform(pdata):
    "translates project data into a structure suitable for terraform"
    #return thread(pdata, ec2, vpc)
    translations = [
        ec2,
        vpc
    ]
    resources = [fn(pdata) for fn in translations]
    resources = list(filter(None, resources))
    return {"resource": resources}
