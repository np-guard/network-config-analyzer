final fw rules for query: connectivity_map_4_md, config: np4:
src ip block: 0.0.0.0/0 dst_ns: [default,ibm-system-new,kube-system-new-dummy-to-ignore] dst_pods: [*] conn: All connections
src ip block: ::/0 dst_ns: [default,ibm-system-new,kube-system-new-dummy-to-ignore] dst_pods: [*] conn: All connections
src_ns: [default,ibm-system-new,kube-system-new,kube-system-new-dummy-to-ignore] src_pods: [*] dst ip block: 0.0.0.0/0 conn: All connections
src_ns: [default,ibm-system-new,kube-system-new,kube-system-new-dummy-to-ignore] src_pods: [*] dst ip block: ::/0 conn: All connections
src_ns: [default,ibm-system-new,kube-system-new,kube-system-new-dummy-to-ignore] src_pods: [*] dst_ns: [default,ibm-system-new,kube-system-new-dummy-to-ignore] dst_pods: [*] conn: All connections
src_ns: [default] src_pods: [*] dst_ns: [kube-system-new] dst_pods: [*] conn: TCP 85-90
src_ns: [ibm-system-new] src_pods: [*] dst_ns: [kube-system-new] dst_pods: [*] conn: TCP 80-90
src_ns: [kube-system-new-dummy-to-ignore] src_pods: [*] dst_ns: [kube-system-new] dst_pods: [*] conn: TCP 80-88

final fw rules for query: connectivity_map_4_md, config: np3:
src ip block: 0.0.0.0/0 dst_ns: [default,ibm-system-new,kube-system-new-dummy-to-ignore] dst_pods: [*] conn: All connections
src ip block: ::/0 dst_ns: [default,ibm-system-new,kube-system-new-dummy-to-ignore] dst_pods: [*] conn: All connections
src_ns: [default,ibm-system-new,kube-system-new,kube-system-new-dummy-to-ignore] src_pods: [*] dst ip block: 0.0.0.0/0 conn: All connections
src_ns: [default,ibm-system-new,kube-system-new,kube-system-new-dummy-to-ignore] src_pods: [*] dst ip block: ::/0 conn: All connections
src_ns: [default,ibm-system-new,kube-system-new,kube-system-new-dummy-to-ignore] src_pods: [*] dst_ns: [default,ibm-system-new,kube-system-new-dummy-to-ignore] dst_pods: [*] conn: All connections
src_ns: [default] src_pods: [*] dst_ns: [kube-system-new] dst_pods: [*] conn: TCP 85-90

