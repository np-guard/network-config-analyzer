|query|src_ns|src_pods|dst_ns|dst_pods|connection|
|---|---|---|---|---|---|
|semantic_diff, config1: new1, config2: old1, key: Added connections between persistent peers||||||
||[demo]|[bank-ui]|[demo]|[account-command]|All but TCP 8080,9090,UDP 8080|
|semantic_diff, config1: new1, config2: old1, key: Removed connections between persistent peers||||||
||[demo]|[account-query]|[demo]|[bank-ui]|All but TCP 8080|

|query|src_ns|src_pods|dst_ns|dst_pods|connection|
|---|---|---|---|---|---|
|semantic_diff, config1: new1a, config2: old1, key: Added connections between persistent peers||||||
||[demo]|[account-query]|[demo]|[bank-ui]|TCP 8080|
||[demo]|[bank-ui]|[demo]|[account-command]|All connections|
|semantic_diff, config1: new1a, config2: old1, key: Removed connections between persistent peers||||||
||[demo]|[account-query]|[demo]|[bank-ui]|UDP 8080|

|query|src_ns|src_pods|dst_ns|dst_pods|connection|
|---|---|---|---|---|---|
|semantic_diff, config1: new2, config2: old2, key: Added connections between persistent peers||||||
||[demo]|[bank-ui]|[demo]|[account-command]|TCP 8080,UDP 9090,SCTP 7070|
|semantic_diff, config1: new2, config2: old2, key: Removed connections between persistent peers||||||
||[demo]|[bank-ui]|[demo]|[account-command]|TCP 8082,UDP 9091|

