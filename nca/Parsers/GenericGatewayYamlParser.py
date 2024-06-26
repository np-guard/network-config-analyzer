#
# Copyright 2020- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#
import re

from nca.CoreDS.MinDFA import MinDFA
from nca.CoreDS.DimensionsManager import DimensionsManager
from nca.CoreDS.Peer import PeerSet
from nca.CoreDS.PortSet import PortSet
from nca.CoreDS.ProtocolSet import ProtocolSet
from nca.CoreDS.ConnectivityProperties import ConnectivityProperties
from nca.Resources.PolicyResources.GatewayPolicy import GatewayPolicyRule
from .GenericYamlParser import GenericYamlParser


class GenericGatewayYamlParser(GenericYamlParser):
    """
    A general parser, common for K8s Ingress resources, as well as for Istio Gateway/VirtualService resources.
    Specific K8s Ingress / Istio Gateway / Istio VirtualService parsers are inherited from this class.
    """

    def __init__(self, peer_container, ingress_file_name=''):
        """
        :param PeerContainer peer_container: The ingress policy will be evaluated against this set of peers
        :param str ingress_file_name: The name of the ingress resource file
        """
        GenericYamlParser.__init__(self, ingress_file_name)
        self.peer_container = peer_container
        self.default_backend_peers = PeerSet()
        self.default_backend_ports = PortSet()

    def parse_regex_host_value(self, regex_value, rule):
        """
        for 'hosts' dimension of type MinDFA -> return a MinDFA, or None for all values
        :param str regex_value: input regex host value
        :param dict rule: the parsed rule object
        :return: Union[MinDFA, None] object
        """
        if regex_value is None:
            return None  # to represent that all is allowed, and this dimension can be inactive in the generated cube

        if regex_value == '*':
            return DimensionsManager().get_dimension_domain_by_name('hosts')

        allowed_chars = "[\\w]"
        allowed_chars_with_star_regex = "[*" + MinDFA.default_dfa_alphabet_chars + "]*"
        if not re.fullmatch(allowed_chars_with_star_regex, regex_value):
            self.syntax_error(f'Illegal characters in host {regex_value}', rule)

        # convert regex_value into regex format supported by greenery
        regex_value = regex_value.replace(".", "[.]")
        if '*' in regex_value:
            if not regex_value.startswith('*'):
                self.syntax_error(f'Illegal host value pattern: {regex_value}')
            regex_value = regex_value.replace("*", allowed_chars + '*')
        return MinDFA.dfa_from_regex(regex_value)

    def parse_host_value(self, host, resource):
        """
        For 'hosts' dimension of type MinDFA -> return a MinDFA, or None for all values
        :param str host: input regex host value
        :param dict resource: the parsed gateway object
        :return: Union[MinDFA, None] object
        """
        namespace_and_name = host.split('/', 1)
        if len(namespace_and_name) > 1:
            self.warning(f'host {host}: namespace is not supported yet. Ignoring the host', resource)
            return None
        return self.parse_regex_host_value(host, resource)

    @staticmethod
    def _make_allow_rules(conn_props, src_peers):
        """
        Make IngressPolicyRules from the given connections
        :param ConnectivityProperties conn_props: the given connections
        :param PeerSet src_peers: the source peers to add to optimized props
        :return: the list of IngressPolicyRules
        """
        res = []
        assert not conn_props.is_active_dimension("src_peers")
        # extract dst_peers dimension from cubes
        tcp_protocol = ProtocolSet.get_protocol_set_with_single_protocol('TCP')
        for cube in conn_props:
            conn_cube = conn_props.get_connectivity_cube(cube)
            new_conn_cube = conn_cube.copy()
            conn_cube.update({"src_peers": src_peers, "protocols": tcp_protocol})
            rule_opt_props = ConnectivityProperties.make_conn_props(conn_cube)
            dst_peer_set = new_conn_cube["dst_peers"]
            new_conn_cube.unset_dim("dst_peers")
            res.append(GatewayPolicyRule(dst_peer_set, rule_opt_props))
        return res

    @staticmethod
    def get_path_prefix_dfa(path_string):
        """
        Given a prefix path, get its MinDFA that accepts all relevant paths
        :param str path_string: a path string from policy, specified as Prefix
        :rtype MinDFA
        """
        if path_string == '/':
            return DimensionsManager().get_dimension_domain_by_name('paths')
        allowed_chars = "[" + MinDFA.default_dfa_alphabet_chars + "]"
        if path_string.endswith('/'):
            path_string = path_string[:-1]
        path_regex = f'{path_string}(/{allowed_chars}*)?'
        return MinDFA.dfa_from_regex(path_regex)
