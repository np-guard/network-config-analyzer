|query|src_ns|src_pods|dst_ns|dst_pods|connection|
|---|---|---|---|---|---|
|semantic_diff, config1: np1, config2: np4, key: Added connections between persistent peers||||||
||[default,kube-system-dummy-to-ignore,vendor-system]|[*]|[kube-system]|[tier=frontend]|All connections|
||[kube-system]|[!has(tier) or tier=not_frontend_for_demo]|[kube-system]|[tier=frontend]|All connections|
|semantic_diff, config1: np1, config2: np4, key: Removed connections between persistent peers||||||
||[kube-system]|[tier=frontend]|[default,kube-system-dummy-to-ignore,vendor-system]|[*]|All connections|
||[kube-system]|[tier=frontend]|[kube-system]|[!has(tier) or tier=not_frontend_for_demo]|All connections|
|semantic_diff, config1: np1, config2: np4, key: Added connections between persistent peers and ipBlocks||||||
|||10.0.0.0/8,172.21.0.0/16,172.30.0.0/16|[kube-system]|[tier=frontend]|All connections|
|||0.0.0.0/0|[kube-system]|[tier=frontend]|All but {protocols:UDP,dst_ports:53}|
|semantic_diff, config1: np1, config2: np4, key: Removed connections between persistent peers and ipBlocks||||||
||[kube-system]|[tier=frontend]||0.0.0.0-49.49.255.255,49.50.0.1,49.50.0.3,49.50.0.5,49.50.0.7,49.50.0.9,49.50.0.11,49.50.0.13,49.50.0.15,49.50.0.17-255.255.255.255|All connections|
