#
# Copyright 2020- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

from dataclasses import dataclass, field
from collections import deque
from sys import stderr
import yaml
from nca.Utils.CmdlineRunner import CmdlineRunner
from nca.Resources.PolicyResources.NetworkPolicy import NetworkPolicy
from nca.Parsers.K8sPolicyYamlParser import K8sPolicyYamlParser
from nca.Parsers.CalicoPolicyYamlParser import CalicoPolicyYamlParser
from nca.Parsers.IstioPolicyYamlParser import IstioPolicyYamlParser
from nca.Parsers.IstioSidecarYamlParser import IstioSidecarYamlParser
from nca.Parsers.IngressPolicyYamlParser import IngressPolicyYamlParser
from nca.Parsers.IstioGatewayYamlParser import IstioGatewayYamlParser
from nca.Parsers.IstioVirtualServiceYamlParser import IstioVirtualServiceYamlParser
from nca.Parsers.IstioGatewayPolicyGenerator import IstioGatewayPolicyGenerator
from nca.Utils.ExplTracker import ExplTracker
from nca.Utils.NcaLogger import NcaLogger
from .NetworkLayer import NetworkLayersContainer, NetworkLayerName


@dataclass
class PoliciesContainer:
    """
    A class for holding policies map and layers map containing sorted policies per layer
    policies: map from tuples (policy name, policy type) to policy objects
    layers: map from layer name to layer object
    """
    policies: dict = field(default_factory=dict)
    layers: NetworkLayersContainer = field(default_factory=NetworkLayersContainer)

    def append_policy(self, policy):
        """
        Add a policy to the container
        :param NetworkPolicy policy: the policy to add
        """
        # validate input policy
        if not policy:
            return
        policy_type = policy.policy_kind
        if policy_type == NetworkPolicy.PolicyType.Unknown:
            raise Exception('Unknown policy type')
        if (policy.full_name(), policy_type) in self.policies:
            warning = f'Warning: policy {policy.full_name()} of type {policy_type} already exists. Ignoring new policy.'
            NcaLogger().log_message(warning, file=stderr)
            return

        # update policies map
        self.policies[(policy.full_name(), policy_type)] = policy
        # add policy to the corresponding layer's list (sorted) of policies
        self.layers.add_policy(policy, NetworkLayerName.policy_type_to_layer(policy_type))


class PoliciesFinder:
    """
    This class is responsible for finding the network policies in the relevant input resources
    The class contains several ways to build the set of policies (from cluster, from file-system, from GitHub).
    """
    def __init__(self):
        self.policies_container = PoliciesContainer()
        self._parse_queue = deque()
        self.peer_container = None
        # following missing resources fields are relevant for "livesim" mode,
        # where certain resources are added to enable the analysis
        self.missing_istio_gw_pods_with_labels = set()
        self.missing_k8s_ingress_peers = False
        self.missing_dns_pods_with_labels = set()

    def set_peer_container(self, peer_container):
        """
        Sets the peer_container class member as it is needed when parsing the policies
        :param Peer Container peer_container: a peer container with all topology objects from the input resources
        """
        self.peer_container = peer_container
        self.peer_container.clear_pods_extra_labels()

    def load_policies_from_buffer(self, buffer):
        self._add_policies(buffer, 'buffer')

    def load_policies_from_k8s_cluster(self):
        self._add_policies(CmdlineRunner.get_k8s_resources(['networkPolicy', 'ingress']), 'kubectl')

    def load_policies_from_calico_cluster(self):
        self._add_policies(CmdlineRunner.get_calico_resources('profile'), 'calicoctl')
        self._add_policies(CmdlineRunner.get_calico_resources('networkPolicy'), 'calicoctl')
        self._add_policies(CmdlineRunner.get_calico_resources('globalNetworkPolicy'), 'calicoctl')

    def load_istio_policies_from_k8s_cluster(self):
        self._add_policies(CmdlineRunner.get_k8s_resources(['authorizationPolicy', 'sidecar', 'Gateway',
                                                            'VirtualService']), 'kubectl')

    def _add_policy(self, policy):
        """
        This should be the only place where we add policies to the config's set of policies from input resources
        :param NetworkPolicy.NetworkPolicy policy: The policy to add
        :return: None
        """
        self.policies_container.append_policy(policy)

    def parse_policies_in_parse_queue(self):  # noqa: C901
        istio_gtw_parser = None
        istio_vs_parser = None
        istio_sidecar_parser = None
        for policy, file_name, policy_type in self._parse_queue:
            parsed_policy = None
            if policy_type == NetworkPolicy.PolicyType.CalicoProfile:
                parsed_element = CalicoPolicyYamlParser(policy, self.peer_container, file_name)
                # only during parsing adding extra labels from profiles (not supporting profiles with rules)
                parsed_policy = parsed_element.parse_policy()
            elif policy_type == NetworkPolicy.PolicyType.K8sNetworkPolicy:
                parsed_element = K8sPolicyYamlParser(policy, self.peer_container, file_name)
                parsed_policy = parsed_element.parse_policy()
                self._add_policy(parsed_policy)
                # add info about missing resources
                self.missing_dns_pods_with_labels.update(parsed_element.missing_pods_with_labels)
            elif policy_type == NetworkPolicy.PolicyType.IstioAuthorizationPolicy:
                parsed_element = IstioPolicyYamlParser(policy, self.peer_container, file_name)
                parsed_policy = parsed_element.parse_policy()
                self._add_policy(parsed_policy)
            elif policy_type == NetworkPolicy.PolicyType.IstioSidecar:
                if not istio_sidecar_parser:
                    istio_sidecar_parser = IstioSidecarYamlParser(policy, self.peer_container, file_name)
                else:
                    istio_sidecar_parser.reset(policy, self.peer_container, file_name)
                istio_sidecar_parser.parse_policy()
            elif policy_type == NetworkPolicy.PolicyType.Ingress:
                parsed_element = IngressPolicyYamlParser(policy, self.peer_container, file_name)
                parsed_policy = parsed_element.parse_policy()
                self._add_policy(parsed_policy)
                # add info about missing resources
                self.missing_k8s_ingress_peers |= parsed_element.missing_k8s_ingress_peers
            elif policy_type == NetworkPolicy.PolicyType.Gateway:
                if not istio_gtw_parser:
                    istio_gtw_parser = IstioGatewayYamlParser(self.peer_container)
                istio_gtw_parser.parse_gateway(policy, file_name)
                # add info about missing resources
                self.missing_istio_gw_pods_with_labels.update(istio_gtw_parser.missing_istio_gw_pods_with_labels)
            elif policy_type == NetworkPolicy.PolicyType.VirtualService:
                if not istio_vs_parser:
                    istio_vs_parser = IstioVirtualServiceYamlParser(self.peer_container)
                istio_vs_parser.parse_virtual_service(policy, file_name)
            else:
                parsed_element = CalicoPolicyYamlParser(policy, self.peer_container, file_name)
                parsed_policy = parsed_element.parse_policy()
                self._add_policy(parsed_policy)
            # the name is sometimes modified when parsed, like in the ingress case, when "allowed" is added
            if ExplTracker().is_active():
                if parsed_policy:
                    policy_name = parsed_policy.name
                    ExplTracker().add_policy_to_peers(parsed_policy)
                else:  # certain istio policies are parsed later (sidecar / virtual-service)
                    policy_name = policy.get('metadata').get('name')
                ExplTracker().add_item(policy.path,
                                       policy.line_number,
                                       policy_name
                                       )
        if istio_gtw_parser or istio_vs_parser:
            if not istio_vs_parser:
                istio_vs_parser = IstioVirtualServiceYamlParser(self.peer_container)
            istio_gtw_policy_gen = IstioGatewayPolicyGenerator(istio_gtw_parser, istio_vs_parser)
            istio_gateway_policies = istio_gtw_policy_gen.create_istio_gateway_policies()
            for istio_traffic_policy in istio_gateway_policies:
                self._add_policy(istio_traffic_policy)
                if ExplTracker().is_active():
                    ExplTracker().add_item(istio_traffic_policy.vs_file_name, istio_traffic_policy.line_number,
                                           istio_traffic_policy.name)
                    ExplTracker().add_policy_to_peers(istio_traffic_policy)
        if istio_sidecar_parser:
            istio_sidecars = istio_sidecar_parser.get_istio_sidecars()
            for istio_sidecar in istio_sidecars:
                self._add_policy(istio_sidecar)
                if ExplTracker().is_active():
                    ExplTracker().add_policy_to_peers(istio_sidecar)

    def parse_yaml_code_for_policy(self, policy_object, file_name):
        policy_type = NetworkPolicy.get_policy_type_from_dict(policy_object)
        if policy_type == NetworkPolicy.PolicyType.Unknown:
            return
        if policy_type == NetworkPolicy.PolicyType.List:
            self._add_policies_to_parse_queue(policy_object.get('items', []), file_name)
        elif policy_type == NetworkPolicy.PolicyType.CalicoProfile:
            self._parse_queue.appendleft((policy_object, file_name, policy_type))  # profiles must be parsed first
        else:
            self._parse_queue.append((policy_object, file_name, policy_type))

    def _add_policies_to_parse_queue(self, policy_list, file_name):
        for policy in policy_list:
            self.parse_yaml_code_for_policy(policy, file_name)

    def _add_policies(self, doc, file_name):
        code = yaml.load_all(doc, Loader=yaml.CSafeLoader)
        for policy_list in code:
            if isinstance(policy_list, dict):
                self._add_policies_to_parse_queue(policy_list.get('items', []), file_name)
            else:  # we got a list of lists, e.g., when combining calico np, gnp and profiles
                for policy_list_list in policy_list:
                    if isinstance(policy_list_list, dict):
                        self._add_policies_to_parse_queue(policy_list_list.get('items', []), file_name)

    def has_empty_containers(self):
        return not self.policies_container.policies

    def rebuild_policies_by_peer_container(self, peer_container):
        result = PoliciesFinder()
        result.peer_container = peer_container
        result._parse_queue = self._parse_queue
        result.parse_policies_in_parse_queue()
        return result
