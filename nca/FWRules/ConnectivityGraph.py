#
# Copyright 2020- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

import itertools
from collections import defaultdict
import networkx
from nca.CoreDS.Peer import IpBlock, Pod
from nca.CoreDS.ProtocolSet import ProtocolSet
from nca.CoreDS.ConnectivityProperties import ConnectivityProperties
from .DotGraph import DotGraph
from .ClusterInfo import ClusterInfo


class ConnectivityGraph:
    """
    Represents a connectivity digraph, that is a set of labeled edges, where the nodes are peers and
    the labels on the edges are the allowed connections between two peers.
    """

    def __init__(self, all_peers, allowed_labels, output_config):
        """
        Create a ConnectivityGraph object
        :param all_peers: PeerSet with the topology all peers (pods and ip blocks)
        :param allowed_labels: the set of allowed labels to be used in generated fw-rules, extracted from policy yamls
        :param output_config: OutputConfiguration object
        """
        # props_to_peers holds the connectivity graph
        self.output_config = output_config
        self.props_to_peers = defaultdict(list)
        if self.output_config.fwRulesOverrideAllowedLabels:
            allowed_labels = set(label for label in self.output_config.fwRulesOverrideAllowedLabels.split(','))
        self.cluster_info = ClusterInfo(all_peers, allowed_labels)
        self.allowed_labels = allowed_labels

    def add_edges_from_cube_dict(self, conn_cube, peer_container, connectivity_restriction=None):
        """
        Add edges to the graph according to the give cube
        :param ConnectivityCube conn_cube: the given cube
         whereas all other values should be filtered out in the output
        :param PeerContainer peer_container: the peer container
        :param Union[str,None] connectivity_restriction: specify if connectivity is restricted to TCP / non-TCP, or not
        """

        relevant_protocols = ProtocolSet()
        if connectivity_restriction:
            if connectivity_restriction == 'TCP':
                relevant_protocols.add_protocol('TCP')
            else:  # connectivity_restriction == 'non-TCP'
                relevant_protocols = ProtocolSet.get_non_tcp_protocols()

        props, src_peers, dst_peers = \
            ConnectivityProperties.extract_src_dst_peers_from_cube(conn_cube, peer_container, relevant_protocols)
        split_src_peers = src_peers.split()
        split_dst_peers = dst_peers.split()
        for src_peer in split_src_peers:
            for dst_peer in split_dst_peers:
                self.props_to_peers[props].append((src_peer, dst_peer))

    def add_props_to_graph(self, props, peer_container, connectivity_restriction=None):
        """
        Add edges to the graph according to the given connectivity properties
        :param ConnectivityProperties props: the given connectivity properties
        :param PeerContainer peer_container: the peer container
        :param Union[str,None] connectivity_restriction: specify if connectivity is restricted to TCP / non-TCP, or not

        """
        for cube in props:
            self.add_edges_from_cube_dict(props.get_connectivity_cube(cube), peer_container, connectivity_restriction)

    def _get_peer_details(self, peer, format_requirement=False):
        """
        Get the name of a peer object for connectivity graph, the type and the namespace
        :param Peer peer: the peer object
        :param bool format_requirement: indicates if to make special changes in str result according to format requirements
        some changes are required for txt_no_fw_rules format: - to print ip_range only for an ipblock
        - replace () with [] for deployment workload_names
        - if the peer has a replicaSet owner, type its full name with [ReplicaSet] regardless its suffix
        :return: tuple(str, str, str, str )
        str: the peer name
        str: the peer type ip_block, livesim, or pod
        str: namespace name
        str: text - the text to present at connectivity graph
        """
        nc_name = peer.namespace.name if peer.namespace else ''
        if isinstance(peer, IpBlock):
            peer_name = peer.get_ip_range_or_cidr_str(format_requirement)
            return peer_name, DotGraph.NodeType.IPBlock, nc_name, [peer_name]
        is_livesim = peer.full_name().endswith('-livesim')
        peer_type = DotGraph.NodeType.Livesim if is_livesim else DotGraph.NodeType.Pod
        if self.output_config.outputEndpoints == 'deployments' and isinstance(peer, Pod):
            peer_name = peer.replicaset_name if format_requirement and peer.replicaset_name else peer.workload_name
            if format_requirement:
                to_replace = {'(': '[', ')': ']'}
                for ch in to_replace:
                    peer_name = peer_name.replace(ch, to_replace[ch])
        else:
            peer_name = str(peer)
        # text = the peer_name after removing the namespace_name from it, if exist
        text = ('/').join([t for t in peer_name.split('/') if t != nc_name])
        return peer_name, peer_type, nc_name, [text]

    @staticmethod
    def reformat_graph(undirected_edges, directed_edges, allow_undirected):
        """
        reformat_graph replace undirected_edges with directed_edges and vice versa
        :param: undirected_edges: set of pairs
        :param: directed_edges: set of pairs
        :param: allow_undirected_edges: bool
        return: truple( set, set)
        set: set of the undirected edges in the graph
        set: set of the directed edges in the graph
        """
        if allow_undirected:
            undirected_edges = set(edge for edge in directed_edges if (edge[1], edge[0]) in directed_edges) | undirected_edges
            directed_edges = directed_edges - undirected_edges
            undirected_edges = set(edge for edge in undirected_edges if edge[1] < edge[0])
        else:
            directed_edges = directed_edges | undirected_edges | set((edge[1], edge[0]) for edge in undirected_edges)
            undirected_edges = set()
        return undirected_edges, directed_edges

    @staticmethod
    def _creates_cliqued_graph(undirected_edges, conn_str):
        """
        A clique is a subset of nodes, where every pair of nodes in the subset has an edge
        This method creates a new graph with cliques. of each clique in the graph:
            1. The original edges of the clique are removed
            2. A clique is represented as one or more new nodes (see comment below*)
            3. All new nodes representing one clique are connected to each other
            4. The original nodes of the clique are connected to one of the clique nodes

        comment: In most cases, when a clique has nodes from different namespaces,
                 the clique will be represent by more than one node.
                 a new node will be created for every namespace


        :param: undirected_edges: list of pairs representing the original graph
        return: truple( list, list, list)
        list: list of the undirected edges left in the graph
        list: list of the new undirected edges representing the cliques
        list: list of the new nodes that was created to represent the cliques

        """
        min_clique_size = 4

        # find cliques in the graph:
        graph = networkx.Graph()
        graph.add_edges_from(undirected_edges)
        cliques = networkx.clique.find_cliques(graph)

        cliques_nodes = []
        cliques_edges = set()
        cliques = sorted([sorted(clique) for clique in cliques])
        for clique in cliques:
            if len(clique) < min_clique_size:
                continue
            clq_namespaces = sorted(set(peer[1] for peer in clique))
            # the list of new nodes of the clique:
            clique_namespaces_nodes = []
            for namespace_name in clq_namespaces:
                clq_namespace_peers = [peer for peer in clique if peer[1] == namespace_name]
                if len(clq_namespace_peers) > 1:
                    # creates a new clique node for the namespace
                    namespace_clique_name = f'clique_{len(cliques_nodes)}'
                    namespace_clique_node = (namespace_clique_name, namespace_name)
                    cliques_nodes.append(namespace_clique_node)
                    clique_namespaces_nodes.append(namespace_clique_node)

                    # adds edges from the new node to the original clique nodes in the namespace
                    cliques_edges |= set((namespace_clique_node, node) for node in clq_namespace_peers)
                else:
                    # if the namespace has only one node, we will not add a new clique node
                    # instead we will add it to the clique new nodes:
                    clique_namespaces_nodes.append(clq_namespace_peers[0])

            if len(clique_namespaces_nodes) > 2:
                # creating one more new node,  out of any namespace, and connect it to all other clique new nodes:
                clique_node_name = f'clique_{conn_str}{len(cliques_nodes)}'
                clique_node = (clique_node_name, '')
                cliques_nodes.append(clique_node)
                cliques_edges |= set((clq_con, clique_node) for clq_con in clique_namespaces_nodes)
            elif len(clique_namespaces_nodes) == 2:
                # if only 2 new nodes - we will just connect them to each other
                cliques_edges.add((clique_namespaces_nodes[0], clique_namespaces_nodes[1]))

            # removing the original edges of the clique:
            undirected_edges = undirected_edges - set(itertools.product(clique, clique))
        return undirected_edges, cliques_edges, cliques_nodes

    @staticmethod
    def _creates_bicliqued_graph(directed_edges, conn_str):
        """
        A biclique is a pair of sets. each node at the firs set as an edge to each node in the second set.
        The algorithm:
        1. for each src_node, find the set of the destination nodes (i.e. dst_sets).
        2. for each dst_set found in (1), find the set of sources that connected to every node in the dst_set (i.e. src_set).
           the (src_set, dst_set) is a biclique
        3. find the best biclique - the biclique that reduce the highest number of edges
        4. remove the biclique from the graph, and go back to (1) till no biclique found

        :param: directed_edges: list of pairs representing the original graph
        return: truple( list, list, list)
        list: list of the directed edges that was left in the graph
        list: list the new bicliques nodes
        list: list the new bicliques edged

        """
        bicliques_nodes = []
        bicliques_edges = set()

        while directed_edges:
            # find dst_sets:
            all_sources = set(edge[0] for edge in directed_edges)
            src_to_dst_set = {src: frozenset(e[1] for e in directed_edges if e[0] == src) for src in all_sources}
            all_dst_set = frozenset(src_to_dst_set.values())

            # find all bicliques:
            all_bicliques = []
            for dst_set in all_dst_set:
                src_set = frozenset(src for src in all_sources if src_to_dst_set[src] >= dst_set)
                all_bicliques.append((src_set, dst_set))
            # find the best biclique:
            bicliques_ranks = {(s, d): len(s) * len(d) - len(s) - len(d) for s, d in all_bicliques}
            if max(bicliques_ranks.values()) < 1:
                break
            best_biclique = max(bicliques_ranks, key=bicliques_ranks.get)

            # create the new biclique, and remove it from the graph:
            directed_edges -= set(itertools.product(best_biclique[0], best_biclique[1]))
            biclique_name = f'biclique_{conn_str}{len(bicliques_nodes)}'
            biclique_node = (biclique_name, '')
            bicliques_nodes.append(biclique_node)
            bicliques_edges |= set((src, biclique_node) for src in best_biclique[0])
            bicliques_edges |= set((biclique_node, dst) for dst in best_biclique[1])
        return directed_edges, bicliques_edges, bicliques_nodes

    @staticmethod
    def _find_equal_groups(peers_edges):
        """
        find set of peers that have the same io edges and the same namespace
        :param: peers_edges: dict peer -> [peer edges]
        return: list
        list: list of lists, each list is a group of peers
        list: list of peers that are not in any group
        """
        groups_dict = defaultdict(list)
        for peer, peer_edges in peers_edges.items():
            groups_dict[(peer.namespace, peer_edges)].append(peer)
        groups = [sorted(peer, key=str) for peer in groups_dict.values() if len(peer) > 1]
        left_out = [peer[0] for peer in groups_dict.values() if len(peer) == 1]
        return groups, left_out

    def _get_equals_groups(self):
        """
        _get_equals_groups find in the graph sets of peers that has the same connections.
        it find two kinds of groups:
        1. set of peers that have the same input and the same output edges
        2. set of peers that have the same input and the same output edges and also connected to each other

        the algorithm:
        1. for each peer, collect the list of input and output edges.
        2. for each peer, add self pointing edge
        3. find group of peers that share the same edges list (the group of kind (2))
        4. remove the peers that are already grouped
        5. remove the self pointing edge
        6. find group of peers that share the same edges list (the group of kind (1))

        return: list( pair(list, list))
        list: list of the pairs, each pair is the group and the self edges of the group
        """
        # for each peer, we get a list of (peer,conn,direction) that it connected to:
        peers_edges = {peer: [] for peer in set(self.cluster_info.all_peers)}
        edges_props = dict()
        for props, peer_pairs in self.props_to_peers.items():
            if not props:
                continue
            for src_peer, dst_peer in peer_pairs:
                if src_peer != dst_peer:
                    peers_edges[src_peer].append((dst_peer, props, False))
                    peers_edges[dst_peer].append((src_peer, props, True))
                    edges_props[(src_peer, dst_peer)] = props
                    edges_props[(dst_peer, src_peer)] = props

        # for each peer, adding a self edge only for connection that the peer already have:
        for peer, peer_edges in peers_edges.items():
            for connection in set(c[1] for c in peer_edges):
                peers_edges[peer].append((peer, connection, False))
                peers_edges[peer].append((peer, connection, True))
        peers_edges = {peer: frozenset(edges) for peer, edges in peers_edges.items()}

        # find groups of peers that are also connected to each other:
        connected_groups, left_out = self._find_equal_groups(peers_edges)
        # for every group, also add the connection of the group (should be only one)
        connected_groups = [(group, edges_props.get((group[0], group[1]), None)) for group in connected_groups]

        # removing the peers of groups that we already found:
        peers_edges = {peer: edges for peer, edges in peers_edges.items() if peer in left_out}
        # removing the self loops:
        peers_edges = {p: frozenset(e for e in p_edges if e[0] != p) for p, p_edges in peers_edges.items()}
        not_connected_groups, left_out = self._find_equal_groups(peers_edges)
        # returning [(group, list of self edges)]
        return connected_groups + [(nc_group, None) for nc_group in not_connected_groups] + [([p], None) for p in left_out]

    def get_connections_without_fw_rules_txt_format(self, connectivity_msg=None, exclude_self_loop_conns=True):
        """
        :param Union[str,None] connectivity_msg: a msg header describing either the type of connectivity (TCP/non-TCP)
            for connectivity-map output with connectivity restriction,
            or the type of connectivity changes for semantic-diff query output
        :param bool exclude_self_loop_conns: indicates if to exclude/ include connections from workload to itself
        - always true for connectivity-map query output
        :rtype: str
        :return: a string of the original peers connectivity graph content (without minimization of fw-rules)
        """
        lines = set()
        for props, peer_pairs in self.props_to_peers.items():
            if not props:
                continue
            for src_peer, dst_peer in peer_pairs:
                if src_peer != dst_peer:
                    src_peer_name = self._get_peer_details(src_peer, True)[0]
                    dst_peer_name = self._get_peer_details(dst_peer, True)[0]
                    # no self-loops: if a peer has different replicas or copies, a connection from it to itself will
                    # not be added either
                    if exclude_self_loop_conns and src_peer_name == dst_peer_name:
                        continue
                    conn_str = props.get_simplified_connections_representation(True)
                    lines.add(f'{src_peer_name} => {dst_peer_name} : {conn_str}')

        lines_list = []
        if connectivity_msg:
            lines_list.append(connectivity_msg)
        lines_list.extend(sorted(list(lines)))
        return '\n'.join(lines_list)

    def get_connectivity_dot_format_str(self, connectivity_restriction=None, simplify_graph=False):
        """
        :param Union[str,None] connectivity_restriction: specify if connectivity is restricted to
               TCP / non-TCP , or not
        :param simplify_graph[bool, False] whether to simplify the dot output graph
        :rtype str
        :return: a string with content of dot format for connectivity graph
        """
        restriction_title = f', for {connectivity_restriction} connections' if connectivity_restriction else ''
        query_title = f'{self.output_config.queryName}/' if self.output_config.queryName else ''
        name = f'{query_title}{self.output_config.configName}{restriction_title}'

        dot_graph = DotGraph(name, do_not_subgraph=simplify_graph)
        peers_groups = self._get_equals_groups()
        # we are going to treat a peers_group as one peer.
        # the first peer in the peers_group is representing the group
        # we will add the text of all the peers in the group to this peer
        for peers_group, group_props in peers_groups:
            peer_name, node_type, nc_name, text = self._get_peer_details(peers_group[0])
            if len(peers_group) > 1:
                text = sorted(set(self._get_peer_details(peer)[3][0] for peer in peers_group))
            # a deployment can be a multi_peer with more than one peer but the same text line
            # in this case, we do not want to set it as MultiPod, so we check the text size and not group size:
            node_type = DotGraph.NodeType.MultiPod if len(text) > 1 else node_type
            dot_graph.add_node(nc_name, peer_name, node_type, text)
            # adding the self edges:
            if len(text) > 1 and group_props:
                conn_str = group_props.get_simplified_connections_representation(True)
                conn_str = conn_str.replace('All connections', 'All')
                dot_graph.add_edge(peer_name, peer_name, label=conn_str, is_dir=False)

        representing_peers = [multi_peer[0][0] for multi_peer in peers_groups]
        for props, peer_pairs in self.props_to_peers.items():
            directed_edges = set()
            # todo - is there a better way to get edge details?
            # we should revisit this code after reformatting connections labels
            conn_str = props.get_simplified_connections_representation(True)
            conn_str = conn_str.replace('All connections', 'All')
            for src_peer, dst_peer in peer_pairs:
                if src_peer != dst_peer and props and src_peer in representing_peers and dst_peer in representing_peers:
                    src_peer_name, _, src_nc, _ = self._get_peer_details(src_peer)
                    dst_peer_name, _, dst_nc, _ = self._get_peer_details(dst_peer)
                    directed_edges.add(((src_peer_name, src_nc), (dst_peer_name, dst_nc)))

            undirected_edges, directed_edges = self.reformat_graph(set(), directed_edges, allow_undirected=True)
            undirected_edges, cliques_edges, new_cliques = self._creates_cliqued_graph(undirected_edges, conn_str)
            undirected_edges, directed_edges = self.reformat_graph(undirected_edges, directed_edges, allow_undirected=False)
            directed_edges, bicliques_edges, new_bicliques = self._creates_bicliqued_graph(directed_edges, conn_str)
            undirected_edges, directed_edges = self.reformat_graph(undirected_edges, directed_edges, allow_undirected=True)

            for peer in new_cliques:
                dot_graph.add_node(subgraph=peer[1], name=peer[0], node_type=DotGraph.NodeType.Clique, label=[conn_str])
            for peer in new_bicliques:
                dot_graph.add_node(subgraph=peer[1], name=peer[0], node_type=DotGraph.NodeType.BiClique, label=[conn_str])
            for edge in directed_edges | bicliques_edges:
                dot_graph.add_edge(src_name=edge[0][0], dst_name=edge[1][0], label=conn_str, is_dir=True)
            for edge in undirected_edges | cliques_edges:
                dot_graph.add_edge(src_name=edge[0][0], dst_name=edge[1][0], label=conn_str, is_dir=False)
        return dot_graph.to_str(self.output_config.outputFormat == 'dot')
