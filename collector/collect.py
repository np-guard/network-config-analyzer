import subprocess


get_ctx = 'kubectl config current-context'
print(get_ctx)
cmdline_process = subprocess.Popen(get_ctx.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
ctx, err = cmdline_process.communicate()
ctx_cluster = ctx.decode("utf-8").replace('/', '-').strip()
print(ctx_cluster)

resources = ['pods', 'namespaces', 'services', 'networkpolicies', 'ingresses', 'ingressclasses', 'authorizationpolicies', 'destinationrules','gateways', 'serviceentries','sidecars','virtualservices' ]

for resource in resources:
    cmd = 'kubectl get ' + resource + ' -A -o yaml'
    cmdline_list = cmd.split(' ')
    print(cmd)
    log = open(ctx_cluster + '_' + resource + '.yaml', 'a')
    cmdline_process = subprocess.Popen(cmdline_list, stdout=log, stderr=subprocess.PIPE)
    out, err = cmdline_process.communicate()
    if len(err) > 0:
        print(err)
