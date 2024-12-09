import subprocess

resources = ['pods', 'namespaces', 'services', 'networkpolicies', 'ingresses', 'ingressclasses', 'authorizationpolicies', 'destinationrules','gateways', 'serviceentries','sidecars','virtualservices' ]

for resource in resources:
    cmd = 'kubectl get ' + resource + ' -A -o yaml' 
    cmdline_list = cmd.split(' ')
    print(cmdline_list)
    log = open(resource + '.yaml', 'a')
    cmdline_process = subprocess.Popen(cmdline_list, stdout=log, stderr=subprocess.PIPE)
    out, err = cmdline_process.communicate()    
    print(err)
