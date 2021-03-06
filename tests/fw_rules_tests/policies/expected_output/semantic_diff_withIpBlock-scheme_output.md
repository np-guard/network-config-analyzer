|query|src_ns|src_pods|dst_ns|dst_pods|connection|
|---|---|---|---|---|---|
|semantic_diff, config1: np1, config2: np2, key: Added connections between persistent peers and ipBlocks||||||
|||ip block: 0.0.0.0/5|[kube-system]|[tier in (frontend)]|TCP 53|
|||ip block: 11.0.0.0/8|[kube-system]|[tier in (frontend)]|TCP 53|
|||ip block: 172.22.0.0/15|[kube-system]|[tier in (frontend)]|TCP 53|
|||ip block: 172.31.0.0/16|[kube-system]|[tier in (frontend)]|TCP 53|
|semantic_diff, config1: np1, config2: np2, key: Removed connections between persistent peers and ipBlocks||||||
|||ip block: 0.0.0.0/5|[kube-system]|[tier in (frontend)]|UDP 53|
|||ip block: 11.0.0.0/8|[kube-system]|[tier in (frontend)]|UDP 53|
|||ip block: 172.22.0.0/15|[kube-system]|[tier in (frontend)]|UDP 53|
|||ip block: 172.31.0.0/16|[kube-system]|[tier in (frontend)]|UDP 53|

|query|src_ns|src_pods|dst_ns|dst_pods|connection|
|---|---|---|---|---|---|
|semantic_diff, config1: np1, config2: np3, key: Added connections between persistent peers and ipBlocks||||||
|||ip block: 0.0.0.0/5|[kube-system]|[tier in (frontend)]|TCP 53|
|||ip block: 11.0.0.0/8|[kube-system]|[tier in (frontend)]|TCP 53|
|||ip block: 172.22.0.0/15|[kube-system]|[tier in (frontend)]|TCP 53|
|||ip block: 172.31.0.0/16|[kube-system]|[tier in (frontend)]|TCP 53|
|semantic_diff, config1: np1, config2: np3, key: Removed connections between persistent peers and ipBlocks||||||
|||ip block: 0.0.0.0/5|[kube-system]|[tier in (frontend)]|UDP 53|
|||ip block: 11.0.0.0/8|[kube-system]|[tier in (frontend)]|UDP 53|
|||ip block: 172.22.0.0/15|[kube-system]|[tier in (frontend)]|UDP 53|
|||ip block: 172.31.0.0/16|[kube-system]|[tier in (frontend)]|UDP 53|



|query|src_ns|src_pods|dst_ns|dst_pods|connection|
|---|---|---|---|---|---|
|semantic_diff, config1: np1, config2: np4, key: Added connections between persistent peers||||||
||[default,kube-system-dummy-to-ignore,vendor-system]|[*]|[kube-system]|[tier in (frontend)]|All connections|
||[kube-system]|[!has(tier) or tier in (not_frontend_for_demo)]|[kube-system]|[tier in (frontend)]|All connections|
|semantic_diff, config1: np1, config2: np4, key: Removed connections between persistent peers||||||
||[kube-system]|[tier in (frontend)]|[default,kube-system-dummy-to-ignore,vendor-system]|[*]|All connections|
||[kube-system]|[tier in (frontend)]|[kube-system]|[!has(tier) or tier in (not_frontend_for_demo)]|All connections|
|semantic_diff, config1: np1, config2: np4, key: Added connections between persistent peers and ipBlocks||||||
|||ip block: 0.0.0.0/5|[kube-system]|[tier in (frontend)]|All but UDP 53|
|||ip block: 11.0.0.0/8|[kube-system]|[tier in (frontend)]|All but UDP 53|
|||ip block: 172.22.0.0/15|[kube-system]|[tier in (frontend)]|All but UDP 53|
|||ip block: 172.31.0.0/16|[kube-system]|[tier in (frontend)]|All but UDP 53|
|||ip block: 10.0.0.0/8|[kube-system]|[tier in (frontend)]|All connections|
|||ip block: 172.21.0.0/16|[kube-system]|[tier in (frontend)]|All connections|
|||ip block: 172.30.0.0/16|[kube-system]|[tier in (frontend)]|All connections|
|||ip block: ::/0|[kube-system]|[tier in (frontend)]|All connections|
|semantic_diff, config1: np1, config2: np4, key: Removed connections between persistent peers and ipBlocks||||||
||[kube-system]|[tier in (frontend)]||ip block: 0.0.0.0/3|All connections|
||[kube-system]|[tier in (frontend)]||ip block: 49.50.0.1/32|All connections|
||[kube-system]|[tier in (frontend)]||ip block: 49.50.0.11/32|All connections|
||[kube-system]|[tier in (frontend)]||ip block: 49.50.0.13/32|All connections|
||[kube-system]|[tier in (frontend)]||ip block: 49.50.0.15/32|All connections|
||[kube-system]|[tier in (frontend)]||ip block: 49.50.0.17/32|All connections|
||[kube-system]|[tier in (frontend)]||ip block: 49.50.0.3/32|All connections|
||[kube-system]|[tier in (frontend)]||ip block: 49.50.0.5/32|All connections|
||[kube-system]|[tier in (frontend)]||ip block: 49.50.0.7/32|All connections|
||[kube-system]|[tier in (frontend)]||ip block: 49.50.0.9/32|All connections|
||[kube-system]|[tier in (frontend)]||ip block: ::/0|All connections|

|query|src_ns|src_pods|dst_ns|dst_pods|connection|
|---|---|---|---|---|---|
|semantic_diff, config1: np1, config2: np2, key: Added connections between persistent peers and ipBlocks||||||
|||ip block: 0.0.0.0/5|[kube-system]|[tier in (frontend)]|TCP 53|
|||ip block: 11.0.0.0/8|[kube-system]|[tier in (frontend)]|TCP 53|
|||ip block: 172.22.0.0/15|[kube-system]|[tier in (frontend)]|TCP 53|
|||ip block: 172.31.0.0/16|[kube-system]|[tier in (frontend)]|TCP 53|
|semantic_diff, config1: np1, config2: np2, key: Removed connections between persistent peers and ipBlocks||||||
|||ip block: 0.0.0.0/5|[kube-system]|[tier in (frontend)]|UDP 53|
|||ip block: 11.0.0.0/8|[kube-system]|[tier in (frontend)]|UDP 53|
|||ip block: 172.22.0.0/15|[kube-system]|[tier in (frontend)]|UDP 53|
|||ip block: 172.31.0.0/16|[kube-system]|[tier in (frontend)]|UDP 53|

