## Scheme file format
A scheme file is a yaml file, specifying what should be checked.
It should contain at least the `networkConfigList` and the `queries` fields.

| Field | Description | Value | Default |
|-------|-------------|-------|---------|
|namespaceList|A globally-scoped list of namespaces in the cluster|directory, git-repo or yaml/json file|Cluster namespaces|
|podList|A globally-scoped list of pods in the cluster|directory, git-repo or yaml/json file|Cluster pods|
|networkConfigList|A list of network configurations and policies to reason about|list of [NetworkConfig](#NetworkConfigobject) objects|
|queries|Queries for the tool to run|list of [Query](#queryobject) objects|

### <a name="NetworkConfigobject"></a>NetworkConfig object
Each NetworkConfig object represents a specific network configuration.
It should contain at least the `name` and the `networkPolicyList` fields.

| Field | Description | Value | Default |
|-------|-------------|-------|---------|
|name   |The name of this NetworkConfig|string|
|namespaceList|A specific list of namespaces|directory, git-repo or yaml/json file|global namespaceList|
|podList|A specific list of pods|directory, git-repo or yaml/json file|global podList|
|networkPolicyList|A list of sources for NetworkPolicies|list of sources |
|expectedWarnings|The expected sum of returned warnings for all resources of this configuration (an error is issued on mismatch)|integer |
|expectedError|indicates if there is an expected error from a networkPolicy|0/1|

Possible entries (sources) in the list under `networkPolicyList` are:
* The string `k8s` - Adds all K8s NetworkPolicies in the cluster to the set
* The string `calico` - Adds all Calico NetworkPolicies and Profiles in the cluster to the set
* The string `istio` - Adds all Istio AuthorizationPolicies in the cluster to the set
* A full path to a yaml file containing NetworkPolicies - Adds all policies in the file
* A full path to a directory - Adds all policies in all files in this directory
* A full path to a directory + `/**` - Adds all policies in all files under this directory recursively
* A URL of a file in a GHE repository - Adds all policies in the file
* A URL of a directory in a GHE repository - Adds all policies in all files in this directory
* A URL of a GHE directory + `/**` - Adds all policies in all files under this directory recursively
* A URL of a GHE repository + `/**` - Adds all policies in all files in this repository

###  <a name="queryobject"></a>Query object
Each query object instructs the tool to run a specific check on one or more sets of policies.

| Field | Description | Value |
|-------|-------------|-------|
|name   |Query name|string|
|emptiness|Checks all NetworkConfigs for empty selectors/rules|list of [config set](#configsets) names|
|redundancy|Checks each set of NetworkConfigs for redundant policies and for redundant rules within each policy|list of [config set](#configsets) names|
|equivalence|Checks semantic equivalence between each pair of NetworkConfigs sets|list of [config set](#configsets) names|
|strongEquivalence|Like equivalence, but comparisons are policy-wise|list of [config set](#configsets) names|
|semanticDiff|Checks semantic diff between each pair of NetworkConfigs sets|list of [config set](#configsets) names|
|forbids|Checks whether the first set denies all connections **explicitly** allowed by the other sets|list of [config set](#configsets) names|
|permits|Checks whether the first set allows all connections **explicitly** allowed by the other sets|list of [config set](#configsets) names|
|interferes|Checks whether any set interferes with the first set|list of [config set](#configsets) names|
|pairwiseInterferes|Checks whether any two sets in the list interfere each other|list of [config set](#configsets) names|
|containment|Checks whether any set is semantically contained in the first set (does not allow additional connections)|list of [config set](#configsets) names|
|twoWayContainment|Checks what are the relations - equivalence, contains, contained, disjoint, neither - between the first set and each of the other sets|list of [config set](#configsets) names|
|disjointness|Reports pairs of policies with overlapping sets of captured pods|list of [config set](#configsets) names|
|vacuity|Checks whether the set of policies changes cluster default behavior|list of [config set](#configsets) names|
|sanity|Checks all NetworkConfigs for sanity check - includes emptiness, vacuity and redundancies|list of [config set](#configsets) names|
|allCaptured|Checks that all pods are captured by at least one NetworkPolicy|list of [config set](#configsets) names|
|expected|The expected sum of returned results by all sub-queries in this query (a warning is issued on mismatch)|integer|

#### <a name="configsets"></a>Config sets
Each entry in the list of config sets should be either
* __Full set__ - The name of a [NetworkConfig object](#NetworkConfigobject) _OR_
* __Single policy__ - Use the form `<set name>/<namespace>/<policy>`.
For example: `my_set/prod_ns/deny_all_policy`

#### Returned value for each sub-query:
* _emptiness_ -  Count of empty selectors/rules found in all sets of policies
* _redundancy_ - Count of redundant policies/rules found in all sets of policies
* _equivalence_ - Count of non-equivalent comparisons
* _strongEquivalence_ - Count of non-equivalent comparisons
* _semanticDiff_ - Count of removed/added connections
* _forbids_ - Count of sets explicitly specifying connections which the first set allows
* _permits_ - Count of sets explicitly specifying connections which the first set denies
* _interferes_ - Count of sets interfering with the first set
* _pairwiseInterference_ - Count of pairs of interfering sets
* _containment_ - Count of sets contained in the first set
* _disjointness_ - Count of policy pairs in each set with overlapping captured pods
* _vacuity_ - Count of vacuous sets
* _sanity_ - Count of sanity issues
* _allCaptured_ - Count of non-captured pods
