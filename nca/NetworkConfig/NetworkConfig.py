#
# Copyright 2020- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

from dataclasses import replace
from nca.CoreDS import Peer
from nca.CoreDS.ConnectivityProperties import ConnectivityProperties
from nca.Resources.PolicyResources.NetworkPolicy import NetworkPolicy, PolicyConnections, PolicyConnectionsFilter
from .NetworkLayer import NetworkLayerName
from .PoliciesFinder import PoliciesFinder
from nca.Utils.ExplTracker import ExplTracker


class NetworkConfig:
    """
    Represents a network configuration - the set of endpoints, their partitioning to namespaces and a set of policies
    that limit the allowed connectivity.
    The class also contains the core algorithm of computing allowed connections between two endpoints.
    """

    def __init__(self, name, peer_container, policies_finder, debug=False):
        """
        :param str name: A name for this config
        :param PeerContainer peer_container: The set of endpoints and their namespaces
        """
        self.name = name
        self.peer_container = peer_container
        self.policies_finder = policies_finder  # keep for Permits/Forbids query, to rebuild by base config
        self.policies_container = policies_finder.policies_container
        self.debug = debug
        self.allowed_labels = None

    def __eq__(self, other):
        if not isinstance(other, NetworkConfig):
            return False
        return self.name == other.name and self.peer_container == other.peer_container and \
            self.policies_container.policies == other.policies_container.policies

    def __str__(self):
        return self.name

    def __bool__(self):
        return bool(self.policies_container.policies)

    def get_num_findings(self):
        """
        :return: The number of findings stored in the policies
        """
        res = 0
        for policy in self.policies_container.policies.values():
            res += len(policy.findings)
        return res

    def find_policy(self, policy_name, required_policy_type=None):
        """
        :param str policy_name: The name of a policy (either fully-qualified or just policy name)
        :param NetworkPolicy.PolicyType required_policy_type: The type of policy to find
        :return: A list of all policy objects matching the policy name
        :rtype: list[NetworkPolicy.NetworkPolicy]
        """
        res = []
        possible_policy_types = [required_policy_type] if required_policy_type else NetworkPolicy.PolicyType
        for policy_type in possible_policy_types:
            if (policy_name, policy_type) in self.policies_container.policies:
                res.append(self.policies_container.policies[(policy_name, policy_type)])
        if not res and policy_name.count('//') == 0:
            for policy in self.policies_container.policies.values():
                policy_type = policy.policy_kind
                if policy_name == policy.name and (not required_policy_type or policy_type == required_policy_type):
                    res.append(policy)
        return res

    def clone_without_policies(self, name):
        """
        :return: A clone of the config without any policies
        :rtype: NetworkConfig
        """
        res = NetworkConfig(name, peer_container=self.peer_container, policies_finder=PoliciesFinder(),
                            debug=self.debug)
        return res

    def clone_without_policy(self, policy_to_exclude):
        """
        :param NetworkPolicy policy_to_exclude: A policy object to exclude from the clone
        :return: A clone of the config having all policies but the one specified
        :rtype: NetworkConfig
        """
        res = self.clone_without_policies(self.name)
        for other_policy in self.policies_container.policies.values():
            if other_policy != policy_to_exclude:
                res.append_policy_to_config(other_policy)
        return res

    def clone_with_just_one_policy(self, name_of_policy_to_include, policy_type=None):
        """
        :param str name_of_policy_to_include: A policy name
        :param NetworkPolicy.PolicyType policy_type: The type of policy to include
        :return: A clone of the config having just a single policy as specified
        :rtype: NetworkConfig
        """
        matching_policies = self.find_policy(name_of_policy_to_include, policy_type)
        if not matching_policies:
            raise Exception(f'No policy named {name_of_policy_to_include} in {self.name}')
        elif len(matching_policies) > 1:
            raise Exception(f'More than one policy named {name_of_policy_to_include} in {self.name}')
        policy = matching_policies[0]

        res = self.clone_without_policies(self.name + '/' + name_of_policy_to_include)
        res.append_policy_to_config(policy)
        return res

    def get_captured_pods(self, layer_name=None):
        """
        Get set of pods for which there exist connectivity resources that can influence their allowed connectivity
        :param NetworkLayerName layer_name: The name of a layer to get the pods from
        :return: All pods captured by any policy, in at least one layer
        :rtype: Peer.PeerSet
        """
        captured_pods = Peer.PeerSet()
        # get all policies list (of all layers) or all policies per input layer
        if layer_name is None:
            policies_list = self.policies_container.policies.values()
        else:
            policies_list = self.policies_container.layers[
                layer_name].policies_list if layer_name in self.policies_container.layers else []

        for policy in policies_list:
            captured_pods |= policy.selected_peers

        return captured_pods

    def get_affected_pods(self, is_ingress, layer_name):
        """
        :param bool is_ingress: Whether we return pods affected for ingress or for egress connection
        :param NetworkLayerName layer_name: The name of the layer to use
        :return: All pods captured by any policy that affects ingress/egress (excluding profiles)
        :rtype: Peer.PeerSet
        """
        affected_pods = Peer.PeerSet()
        policies_list = self.policies_container.layers[layer_name].policies_list
        for policy in policies_list:
            if (is_ingress and policy.affects_ingress) or (not is_ingress and policy.affects_egress):
                affected_pods |= policy.selected_peers

        return affected_pods

    def check_for_excluding_ipv6_addresses(self, exclude_ipv6):
        """
        checks and returns if to exclude non-referenced IPv6 addresses from the config
        Excluding the IPv6 addresses will be enabled if the exclude_ipv6 param is True and
        IPv6 addresses in all the policies of the config (if existed) were added automatically by the parser
        and not referenced by user
        :param bool exclude_ipv6: indicates if to exclude ipv_6 non-referenced addresses
        :rtype bool
        """
        if not exclude_ipv6:
            return False

        for policy in self.policies_container.policies.values():
            if policy.has_ipv6_addresses:  # if at least one policy has referenced ipv6 addresses, ipv6 will be included
                return False
        return True  # getting here means all policies didn't reference ipv6, it is safe to exclude ipv6 addresses

    def get_allowed_labels(self):
        if self.allowed_labels is not None:
            return self.allowed_labels
        self.allowed_labels = set()
        for policy in self.policies_container.policies.values():
            self.allowed_labels |= policy.referenced_labels
        return self.allowed_labels

    def allowed_connections(self, layer_name=None, res_conns_filter=PolicyConnectionsFilter()):
        """
        Computes the set of allowed connections between any relevant peers.
        :param NetworkLayerName layer_name: The name of the layer to use, if requested to use a specific layer only
        :param PolicyConnectionsFilter res_conns_filter: filter of the required resulting connections
        (connections with False value will not be calculated)
        :return: allowed_conns: all allowed connections for relevant peers.
        :rtype: PolicyConnections
        """
        if ExplTracker().is_active():
            ExplTracker().set_peers(self.peer_container.peer_set)
        if layer_name is not None:
            if layer_name not in self.policies_container.layers:
                return self.policies_container.layers.empty_layer_allowed_connections(self.peer_container,
                                                                                      layer_name,
                                                                                      res_conns_filter)
            return self.policies_container.layers[layer_name].allowed_connections(self.peer_container,
                                                                                  res_conns_filter)

        all_peers = self.peer_container.get_all_peers_group()
        host_eps = Peer.PeerSet(set([peer for peer in all_peers if isinstance(peer, Peer.HostEP)]))
        # all possible connections involving hostEndpoints
        conn_hep = ConnectivityProperties.make_conn_props_from_dict({"src_peers": host_eps}) | \
            ConnectivityProperties.make_conn_props_from_dict({"dst_peers": host_eps})
        if host_eps and NetworkLayerName.K8s_Calico not in self.policies_container.layers:
            # maintain K8s_Calico layer as active if peer container has hostEndpoint
            conns_res = \
                self.policies_container.layers.empty_layer_allowed_connections(self.peer_container,
                                                                               NetworkLayerName.K8s_Calico,
                                                                               res_conns_filter)
            conns_res.and_by_filter(conn_hep, replace(res_conns_filter, calc_all_allowed=False))
        else:
            conns_res = PolicyConnections()
            if res_conns_filter.calc_all_allowed:
                conns_res.all_allowed_conns = ConnectivityProperties.get_all_conns_props_per_config_peers(self.peer_container)
        for layer, layer_obj in self.policies_container.layers.items():
            conns_per_layer = layer_obj.allowed_connections(self.peer_container, res_conns_filter)
            # only K8s_Calico layer handles host_eps
            if layer != NetworkLayerName.K8s_Calico:
                # connectivity of hostEndpoints is only determined by calico layer
                conns_per_layer.sub_by_filter(conn_hep, replace(res_conns_filter, calc_all_allowed=False))
            conns_res.captured |= conns_per_layer.captured
            if res_conns_filter.calc_all_allowed:
                # all allowed connections: intersection of all allowed connections from all layers
                conns_res.all_allowed_conns &= conns_per_layer.all_allowed_conns
            if res_conns_filter.calc_allowed:
                # all allowed captured connections: should be captured by at least one layer
                conns_res.allowed_conns |= conns_per_layer.allowed_conns
            if res_conns_filter.calc_denied:
                # denied conns: should be denied by at least one layer
                conns_res.denied_conns |= conns_per_layer.denied_conns

        if res_conns_filter.calc_allowed:
            # allowed captured conn (by at least one layer) has to be allowed by all layers (either implicitly or explicitly)
            conns_res.allowed_conns &= conns_res.all_allowed_conns
        return conns_res

    def append_policy_to_config(self, policy):
        """
        appends a policy to an existing config
        :param NetworkPolicy.NetworkPolicy policy: The policy to append
        :return: None
        """
        self.policies_container.append_policy(policy)

    def filter_conns_by_peer_types(self, conns):
        """
        Filter the given connections by removing several connection kinds that are never allowed
        (such as IpBlock to IpBlock connections, connections from DNSEntries, and more).
        :param ConnectivityProperties conns: the given connections.
        :return The resulting connections.
        :rtype ConnectivityProperties
        """
        res = conns
        # avoid IpBlock -> {IpBlock, DNSEntry} connections
        all_ips = Peer.IpBlock.get_all_ips_block_peer_set()
        all_dns_entries = self.peer_container.get_all_dns_entries()
        ip_to_ip_or_dns_conns = ConnectivityProperties.make_conn_props_from_dict({"src_peers": all_ips,
                                                                                  "dst_peers": all_ips | all_dns_entries})
        res -= ip_to_ip_or_dns_conns
        # avoid DNSEntry->anything connections
        dns_to_any_conns = ConnectivityProperties.make_conn_props_from_dict({"src_peers": all_dns_entries})
        res -= dns_to_any_conns
        return res

    def rebuild_by_base_config_resources(self, base_config):
        """
        Rebuild the current config policies, based on peer_set from the given config,
        and return the result in a new config.
        :param NetworkConfig base_config: The given config, whose peer_set should be used for the resulting config.
        :return NetworkConfig: the resulting config
        """
        result = base_config.clone_without_policies(self.name)
        result.policies_finder = \
            self.policies_finder.rebuild_policies_by_peer_container(result.peer_container)
        result.policies_container = result.policies_finder.policies_container
        return result
