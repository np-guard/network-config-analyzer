
|query|src_ns|src_pods|dst_ns|dst_pods|connection|
|---|---|---|---|---|---|
|semantic_diff, config1: config_a, config2: config_b, key: Lost connections between removed peers||||||
||[default]|[app in (app-3)]|[default]|[app in (app-4)]|All connections|
||[default]|[app in (app-4)]|[default]|[app in (app-3)]|All connections|
|semantic_diff, config1: config_a, config2: config_b, key: Lost connections between removed peers and ipBlocks||||||
|||ip block: 0.0.0.0/0|[default]|[app in (app-3,app-4)]|All connections|
|||ip block: ::/0|[default]|[app in (app-3,app-4)]|All connections|
||[default]|[app in (app-3,app-4)]||ip block: 0.0.0.0/0|All connections|
||[default]|[app in (app-3,app-4)]||ip block: ::/0|All connections|
|semantic_diff, config1: config_a, config2: config_b, key: Lost connections between removed peers and persistent peers||||||
||[default]|[app in (app-3,app-4)]|[default]|[app in (app-0,app-2)]|All connections|
||[default]|[app not in (app-3,app-4)]|[default]|[app in (app-3,app-4)]|All connections|
|semantic_diff, config1: config_a, config2: config_b, key: Added connections between persistent peers||||||
||[default]|[app in (app-0)]|[default]|[app in (app-1)]|All connections|
|semantic_diff, config1: config_a, config2: config_b, key: Removed connections between persistent peers||||||
||[default]|[app in (app-0)]|[default]|[app in (app-2)]|All connections|
|semantic_diff, config1: config_a, config2: config_b, key: Added connections between persistent peers and ipBlocks||||||
|||ip block: 0.0.0.0/0|[default]|[app in (app-1)]|All connections|
|||ip block: ::/0|[default]|[app in (app-1)]|All connections|
|semantic_diff, config1: config_a, config2: config_b, key: Removed connections between persistent peers and ipBlocks||||||
|||ip block: 0.0.0.0/0|[default]|[app in (app-2)]|All connections|
|||ip block: ::/0|[default]|[app in (app-2)]|All connections|
|semantic_diff, config1: config_a, config2: config_b, key: New connections between persistent peers and added peers||||||
||[default]|[app in (app-5,app-6)]|[default]|[app in (app-0,app-1)]|All connections|
||[default]|[app not in (app-5,app-6)]|[default]|[app in (app-5,app-6)]|All connections|
|semantic_diff, config1: config_a, config2: config_b, key: New connections between added peers||||||
||[default]|[app in (app-5)]|[default]|[app in (app-6)]|All connections|
||[default]|[app in (app-6)]|[default]|[app in (app-5)]|All connections|
|semantic_diff, config1: config_a, config2: config_b, key: New connections between added peers and ipBlocks||||||
|||ip block: 0.0.0.0/0|[default]|[app in (app-5,app-6)]|All connections|
|||ip block: ::/0|[default]|[app in (app-5,app-6)]|All connections|
||[default]|[app in (app-5,app-6)]||ip block: 0.0.0.0/0|All connections|
||[default]|[app in (app-5,app-6)]||ip block: ::/0|All connections|

|query|src_ns|src_pods|dst_ns|dst_pods|connection|
|---|---|---|---|---|---|
|semantic_diff, config1: config_b, config2: config_a, key: Lost connections between removed peers||||||
||[default]|[app in (app-5)]|[default]|[app in (app-6)]|All connections|
||[default]|[app in (app-6)]|[default]|[app in (app-5)]|All connections|
|semantic_diff, config1: config_b, config2: config_a, key: Lost connections between removed peers and ipBlocks||||||
|||ip block: 0.0.0.0/0|[default]|[app in (app-5,app-6)]|All connections|
|||ip block: ::/0|[default]|[app in (app-5,app-6)]|All connections|
||[default]|[app in (app-5,app-6)]||ip block: 0.0.0.0/0|All connections|
||[default]|[app in (app-5,app-6)]||ip block: ::/0|All connections|
|semantic_diff, config1: config_b, config2: config_a, key: Lost connections between removed peers and persistent peers||||||
||[default]|[app in (app-5,app-6)]|[default]|[app in (app-0,app-1)]|All connections|
||[default]|[app not in (app-5,app-6)]|[default]|[app in (app-5,app-6)]|All connections|
|semantic_diff, config1: config_b, config2: config_a, key: Added connections between persistent peers||||||
||[default]|[app in (app-0)]|[default]|[app in (app-2)]|All connections|
|semantic_diff, config1: config_b, config2: config_a, key: Removed connections between persistent peers||||||
||[default]|[app in (app-0)]|[default]|[app in (app-1)]|All connections|
|semantic_diff, config1: config_b, config2: config_a, key: Added connections between persistent peers and ipBlocks||||||
|||ip block: 0.0.0.0/0|[default]|[app in (app-2)]|All connections|
|||ip block: ::/0|[default]|[app in (app-2)]|All connections|
|semantic_diff, config1: config_b, config2: config_a, key: Removed connections between persistent peers and ipBlocks||||||
|||ip block: 0.0.0.0/0|[default]|[app in (app-1)]|All connections|
|||ip block: ::/0|[default]|[app in (app-1)]|All connections|
|semantic_diff, config1: config_b, config2: config_a, key: New connections between persistent peers and added peers||||||
||[default]|[app in (app-3,app-4)]|[default]|[app in (app-0,app-2)]|All connections|
||[default]|[app not in (app-3,app-4)]|[default]|[app in (app-3,app-4)]|All connections|
|semantic_diff, config1: config_b, config2: config_a, key: New connections between added peers||||||
||[default]|[app in (app-3)]|[default]|[app in (app-4)]|All connections|
||[default]|[app in (app-4)]|[default]|[app in (app-3)]|All connections|
|semantic_diff, config1: config_b, config2: config_a, key: New connections between added peers and ipBlocks||||||
|||ip block: 0.0.0.0/0|[default]|[app in (app-3,app-4)]|All connections|
|||ip block: ::/0|[default]|[app in (app-3,app-4)]|All connections|
||[default]|[app in (app-3,app-4)]||ip block: 0.0.0.0/0|All connections|
||[default]|[app in (app-3,app-4)]||ip block: ::/0|All connections|

|query|src_ns|src_pods|dst_ns|dst_pods|connection|
|---|---|---|---|---|---|
|semantic_diff, config1: old1, config2: config_a, key: Lost connections between removed peers||||||
||[default,kube-system,vendor-system]|[*]|[default,kube-system,vendor-system]|[*]|All connections|
|semantic_diff, config1: old1, config2: config_a, key: Lost connections between removed peers and ipBlocks||||||
|||ip block: 0.0.0.0/0|[default,kube-system,vendor-system]|[*]|All connections|
|||ip block: ::/0|[default,kube-system,vendor-system]|[*]|All connections|
||[default,kube-system,vendor-system]|[*]||ip block: 0.0.0.0/0|All connections|
||[default,kube-system,vendor-system]|[*]||ip block: ::/0|All connections|
|semantic_diff, config1: old1, config2: config_a, key: New connections between added peers||||||
||[default]|[*]|[default]|[app not in (app-1)]|All connections|
||[default]|[app in (app-1,app-2)]|[default]|[*]|All connections|
|semantic_diff, config1: old1, config2: config_a, key: New connections between added peers and ipBlocks||||||
|||ip block: 0.0.0.0/0|[default]|[app not in (app-1)]|All connections|
|||ip block: ::/0|[default]|[app not in (app-1)]|All connections|
||[default]|[*]||ip block: 0.0.0.0/0|All connections|
||[default]|[*]||ip block: ::/0|All connections|

|query|src_ns|src_pods|dst_ns|dst_pods|connection|
|---|---|---|---|---|---|
|semantic_diff, config1: np1, config2: np2, key: Added connections between persistent peers and ipBlocks||||||
|||ip block: 0.0.0.0/5|[kube-system]|[has(tier)]|TCP 53|
|||ip block: 11.0.0.0/8|[kube-system]|[has(tier)]|TCP 53|
|||ip block: 172.22.0.0/15|[kube-system]|[has(tier)]|TCP 53|
|||ip block: 172.31.0.0/16|[kube-system]|[has(tier)]|TCP 53|
|semantic_diff, config1: np1, config2: np2, key: Removed connections between persistent peers and ipBlocks||||||
|||ip block: 0.0.0.0/5|[kube-system]|[has(tier)]|UDP 53|
|||ip block: 11.0.0.0/8|[kube-system]|[has(tier)]|UDP 53|
|||ip block: 172.22.0.0/15|[kube-system]|[has(tier)]|UDP 53|
|||ip block: 172.31.0.0/16|[kube-system]|[has(tier)]|UDP 53|

|query|src_ns|src_pods|dst_ns|dst_pods|connection|
|---|---|---|---|---|---|
|semantic_diff, config1: config_a_with_ipBlock, config2: config_b_with_ipBlock, key: Lost connections between removed peers||||||
||[default]|[app in (app-3)]|[default]|[app in (app-4)]|All connections|
||[default]|[app in (app-4)]|[default]|[app in (app-3)]|All connections|
|semantic_diff, config1: config_a_with_ipBlock, config2: config_b_with_ipBlock, key: Lost connections between removed peers and ipBlocks||||||
|||ip block: 0.0.0.0/0|[default]|[app in (app-3,app-4)]|All connections|
|||ip block: ::/0|[default]|[app in (app-3,app-4)]|All connections|
||[default]|[app in (app-3,app-4)]||ip block: 0.0.0.0/0|All connections|
||[default]|[app in (app-3,app-4)]||ip block: ::/0|All connections|
|semantic_diff, config1: config_a_with_ipBlock, config2: config_b_with_ipBlock, key: Lost connections between removed peers and persistent peers||||||
||[default]|[app in (app-3,app-4)]|[default]|[app in (app-0,app-2)]|All connections|
||[default]|[app not in (app-3,app-4)]|[default]|[app in (app-3,app-4)]|All connections|
|semantic_diff, config1: config_a_with_ipBlock, config2: config_b_with_ipBlock, key: Added connections between persistent peers||||||
||[default]|[app in (app-0)]|[default]|[app in (app-1)]|All connections|
|semantic_diff, config1: config_a_with_ipBlock, config2: config_b_with_ipBlock, key: Removed connections between persistent peers||||||
||[default]|[app in (app-0)]|[default]|[app in (app-2)]|All connections|
|semantic_diff, config1: config_a_with_ipBlock, config2: config_b_with_ipBlock, key: Added connections between persistent peers and ipBlocks||||||
|||ip block: 0.0.0.0/5|[default]|[app in (app-1)]|All connections|
|||ip block: 10.10.0.0/16|[default]|[app in (app-1)]|All connections|
|||ip block: 11.0.0.0/8|[default]|[app in (app-1)]|All connections|
|||ip block: ::/0|[default]|[app in (app-1)]|All connections|
|semantic_diff, config1: config_a_with_ipBlock, config2: config_b_with_ipBlock, key: Removed connections between persistent peers and ipBlocks||||||
|||ip block: 10.0.0.0/13|[default]|[app in (app-2)]|All but UDP 53|
|||ip block: 10.12.0.0/14|[default]|[app in (app-2)]|All but UDP 53|
|||ip block: 0.0.0.0/5|[default]|[app in (app-2)]|All connections|
|||ip block: 10.11.0.0/16|[default]|[app in (app-2)]|All connections|
|||ip block: 11.0.0.0/8|[default]|[app in (app-2)]|All connections|
|||ip block: ::/0|[default]|[app in (app-2)]|All connections|
|semantic_diff, config1: config_a_with_ipBlock, config2: config_b_with_ipBlock, key: New connections between persistent peers and added peers||||||
||[default]|[app in (app-5,app-6)]|[default]|[app in (app-0,app-1)]|All connections|
||[default]|[app not in (app-5,app-6)]|[default]|[app in (app-5,app-6)]|All connections|
|semantic_diff, config1: config_a_with_ipBlock, config2: config_b_with_ipBlock, key: New connections between added peers||||||
||[default]|[app in (app-5)]|[default]|[app in (app-6)]|All connections|
||[default]|[app in (app-6)]|[default]|[app in (app-5)]|All connections|
|semantic_diff, config1: config_a_with_ipBlock, config2: config_b_with_ipBlock, key: New connections between added peers and ipBlocks||||||
|||ip block: 0.0.0.0/0|[default]|[app in (app-5,app-6)]|All connections|
|||ip block: ::/0|[default]|[app in (app-5,app-6)]|All connections|
||[default]|[app in (app-5,app-6)]||ip block: 0.0.0.0/0|All connections|
||[default]|[app in (app-5,app-6)]||ip block: ::/0|All connections|

