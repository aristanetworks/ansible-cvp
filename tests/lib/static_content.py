#!/usr/bin/env python
# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
# pylint: disable = duplicate-code
# flake8: noqa: R0801
#


"""
cvaas_content - Generic data to load in different tests.
"""


CONFIGLET_CONTENT = """
!RANCID-CONTENT-TYPE: arista
!
daemon TerminAttr
   exec /usr/bin/TerminAttr -cvaddr=10.73.254.1:9910 -cvvrf=MGMT -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent -taillogs
   no shutdown
!
vlan internal order ascending range 1006 1199
!
no ip igmp snooping vlan 111
no ip igmp snooping vlan 112
!
transceiver qsfp default-mode 4x10G
!
service routing protocols model multi-agent
!
hostname EAPI-LEAF1A
ip name-server vrf MGMT 10.73.1.254
ip name-server vrf MGMT 10.73.254.253
!
ntp local-interface vrf MGMT Management1
ntp server vrf MGMT 10.73.254.253 prefer
ntp server vrf MGMT 10.73.1.254
!
snmp-server community inetsix-ro view test rw inetsix-snmp-acl
!
spanning-tree mode mstp
no spanning-tree vlan-id 4093-4094
spanning-tree mst 0 priority 4096
!
aaa authorization exec default local
!
no aaa root
no enable password
!
username admin privilege 15 role network-admin nopassword
username ansible privilege 15 role network-admin secret sha512 $6$Dzu11L7yp9j3nCM9$FSptxMPyIL555OMO.ldnjDXgwZmrfMYwHSr0uznE5Qoqvd9a6UdjiFcJUhGLtvXVZR1r.A/iF5aAt50hf/EK4/
username cvpadmin privilege 15 role network-admin secret sha512 $6$rZKcbIZ7iWGAWTUM$TCgDn1KcavS0s.OV8lacMTUkxTByfzcGlFlYUWroxYuU7M/9bIodhRO7nXGzMweUxvbk8mJmQl8Bh44cRktUj.
username demo privilege 15 role network-admin secret sha512 $6$Dzu11L7yp9j3nCM9$FSptxMPyIL555OMO.ldnjDXgwZmrfMYwHSr0uznE5Qoqvd9a6UdjiFcJUhGLtvXVZR1r.A/iF5aAt50hf/EK4/
!
clock timezone Europe/Paris
!
vlan 110
   name PR01-DEMO
!
vlan 111
   name PR01-TRUST
!
vlan 112
   name PR01-TRUST
!
vlan 131
   name vl131_no_vni
!
vlan 201
   name B-ELAN-201
!
vlan 3010
   name MLAG_iBGP_TENANT_A_PROJECT01
   trunk group LEAF_PEER_L3
!
vlan 3012
   name MLAG_iBGP_PURE_TYPE5
   trunk group LEAF_PEER_L3
!
vlan 4093
   name LEAF_PEER_L3
   trunk group LEAF_PEER_L3
!
vlan 4094
   name MLAG_PEER
   trunk group MLAG
!
vrf instance MGMT
!
vrf instance PURE_TYPE5
!
vrf instance TENANT_A_PROJECT01
!
interface Port-Channel3
   description MLAG_PEER_EAPI-LEAF1B_Po3
   no shutdown
   switchport
   switchport trunk allowed vlan 2-4094
   switchport mode trunk
   switchport trunk group LEAF_PEER_L3
   switchport trunk group MLAG
!
interface Port-Channel5
   description EAPI-AGG01_Po1
   no shutdown
   switchport
   switchport trunk allowed vlan 110-112,131,201
   switchport mode trunk
   mlag 5
!
interface Ethernet1
   description P2P_LINK_TO_EAPI-SPINE1_Ethernet1
   no shutdown
   mtu 1500
   no switchport
   ip address 172.31.255.1/31
!
interface Ethernet2
   description P2P_LINK_TO_EAPI-SPINE2_Ethernet1
   no shutdown
   mtu 1500
   no switchport
   ip address 172.31.255.3/31
!
interface Ethernet3
   description MLAG_PEER_EAPI-LEAF1B_Ethernet3
   no shutdown
   channel-group 3 mode active
!
interface Ethernet4
   description MLAG_PEER_EAPI-LEAF1B_Ethernet4
   no shutdown
   channel-group 3 mode active
!
interface Ethernet5
   description EAPI-AGG01_Ethernet1
   no shutdown
   channel-group 5 mode active
!
interface Loopback0
   description EVPN_Overlay_Peering
   no shutdown
   ip address 192.168.255.3/32
!
interface Loopback1
   description VTEP_VXLAN_Tunnel_Source
   no shutdown
   ip address 192.168.254.3/32
!
interface Management1
   description oob_management
   no shutdown
   vrf MGMT
   ip address 10.73.254.11/24
!
interface Vlan110
   description PR01-DEMO
   no shutdown
   vrf TENANT_A_PROJECT01
   ip address virtual 10.1.10.254/24
!
interface Vlan111
   description PR01-TRUST
   no shutdown
   vrf TENANT_A_PROJECT01
   ip address virtual 10.1.11.254/24
   ip helper-address 1.1.1.1 vrf TEST source-interface lo100
!
interface Vlan112
   description PR01-TRUST
   no shutdown
   vrf TENANT_A_PROJECT01
   ip address virtual 10.1.12.254/24
!
interface Vlan131
   description vl131_no_vni
   no shutdown
   vrf PURE_TYPE5
   ip address virtual 10.1.31.254/24
!
interface Vlan3010
   description MLAG_PEER_L3_iBGP: vrf TENANT_A_PROJECT01
   no shutdown
   mtu 1500
   vrf TENANT_A_PROJECT01
   ip address 172.31.253.2/31
!
interface Vlan3012
   description MLAG_PEER_L3_iBGP: vrf PURE_TYPE5
   no shutdown
   mtu 1500
   vrf PURE_TYPE5
   ip address 172.31.253.2/31
!
interface Vlan4093
   description MLAG_PEER_L3_PEERING
   no shutdown
   mtu 1500
   ip address 172.31.253.2/31
!
interface Vlan4094
   description MLAG_PEER
   no shutdown
   mtu 1500
   no autostate
   ip address 172.31.253.0/31
!
interface Vxlan1
   description EAPI-LEAF1A_VTEP
   vxlan source-interface Loopback1
   vxlan virtual-router encapsulation mac-address mlag-system-id
   vxlan udp-port 4789
   vxlan vlan 110 vni 10110
   vxlan vlan 111 vni 10111
   vxlan vlan 112 vni 10112
   vxlan vlan 201 vni 20201
   vxlan vrf PURE_TYPE5 vni 13
   vxlan vrf TENANT_A_PROJECT01 vni 11
!
ip virtual-router mac-address 00:1c:73:00:dc:01
!
ip routing
no ip routing vrf MGMT
ip routing vrf PURE_TYPE5
ip routing vrf TENANT_A_PROJECT01
!
ip prefix-list PL-LOOPBACKS-EVPN-OVERLAY
   seq 10 permit 192.168.255.0/24 eq 32
   seq 20 permit 192.168.254.0/24 eq 32
!
mlag configuration
   domain-id EAPI_LEAF1
   local-interface Vlan4094
   peer-address 172.31.253.1
   peer-link Port-Channel3
   reload-delay mlag 300
   reload-delay non-mlag 330
!
ip route vrf MGMT 0.0.0.0/0 10.73.254.253
!
route-map RM-CONN-2-BGP permit 10
   match ip address prefix-list PL-LOOPBACKS-EVPN-OVERLAY
!
route-map RM-MLAG-PEER-IN permit 10
   description Make routes learned over MLAG Peer-link less preferred on spines to ensure optimal routing
   set origin incomplete
!
router bfd
   multihop interval 1200 min-rx 1200 multiplier 3
!
router bgp 65101
   router-id 192.168.255.3
   no bgp default ipv4-unicast
   distance bgp 20 200 200
   graceful-restart restart-time 300
   graceful-restart
   maximum-paths 4 ecmp 4
   neighbor EVPN-OVERLAY-PEERS peer group
   neighbor EVPN-OVERLAY-PEERS update-source Loopback0
   neighbor EVPN-OVERLAY-PEERS bfd
   neighbor EVPN-OVERLAY-PEERS ebgp-multihop 3
   neighbor EVPN-OVERLAY-PEERS password 7 q+VNViP5i4rVjW1cxFv2wA==
   neighbor EVPN-OVERLAY-PEERS send-community
   neighbor EVPN-OVERLAY-PEERS maximum-routes 0
   neighbor IPv4-UNDERLAY-PEERS peer group
   neighbor IPv4-UNDERLAY-PEERS password 7 AQQvKeimxJu+uGQ/yYvv9w==
   neighbor IPv4-UNDERLAY-PEERS send-community
   neighbor IPv4-UNDERLAY-PEERS maximum-routes 12000
   neighbor MLAG-IPv4-UNDERLAY-PEER peer group
   neighbor MLAG-IPv4-UNDERLAY-PEER remote-as 65101
   neighbor MLAG-IPv4-UNDERLAY-PEER next-hop-self
   neighbor MLAG-IPv4-UNDERLAY-PEER password 7 vnEaG8gMeQf3d3cN6PktXQ==
   neighbor MLAG-IPv4-UNDERLAY-PEER send-community
   neighbor MLAG-IPv4-UNDERLAY-PEER maximum-routes 12000
   neighbor MLAG-IPv4-UNDERLAY-PEER route-map RM-MLAG-PEER-IN in
   neighbor 172.31.253.3 peer group MLAG-IPv4-UNDERLAY-PEER
   neighbor 172.31.253.3 description EAPI-LEAF1B
   neighbor 172.31.255.0 peer group IPv4-UNDERLAY-PEERS
   neighbor 172.31.255.0 remote-as 65001
   neighbor 172.31.255.0 description EAPI-SPINE1_Ethernet1
   neighbor 172.31.255.2 peer group IPv4-UNDERLAY-PEERS
   neighbor 172.31.255.2 remote-as 65001
   neighbor 172.31.255.2 description EAPI-SPINE2_Ethernet1
   neighbor 192.168.0.2 peer group EVPN-OVERLAY-PEERS
   neighbor 192.168.0.2 remote-as 65000
   neighbor 192.168.0.2 description EAPI-RS01
   neighbor 192.168.0.3 peer group EVPN-OVERLAY-PEERS
   neighbor 192.168.0.3 remote-as 65000
   neighbor 192.168.0.3 description EAPI-RS02
   redistribute connected route-map RM-CONN-2-BGP
   !
   vlan-aware-bundle B-ELAN-201
      rd 192.168.255.3:20201
      route-target both 20201:20201
      redistribute learned
      vlan 201
   !
   vlan-aware-bundle TENANT_A_PROJECT01
      rd 192.168.255.3:11
      route-target both 11:11
      redistribute learned
      vlan 110-112
   !
   address-family evpn
      neighbor EVPN-OVERLAY-PEERS activate
   !
   address-family ipv4
      no neighbor EVPN-OVERLAY-PEERS activate
      neighbor IPv4-UNDERLAY-PEERS activate
      neighbor MLAG-IPv4-UNDERLAY-PEER activate
   !
   vrf PURE_TYPE5
      rd 192.168.255.3:13
      route-target import evpn 13:13
      route-target export evpn 13:13
      router-id 192.168.255.3
      neighbor 172.31.253.3 peer group MLAG-IPv4-UNDERLAY-PEER
      redistribute connected
   !
   vrf TENANT_A_PROJECT01
      rd 192.168.255.3:11
      route-target import evpn 11:11
      route-target export evpn 11:11
      router-id 192.168.255.3
      neighbor 172.31.253.3 peer group MLAG-IPv4-UNDERLAY-PEER
      redistribute connected
      redistribute static
!
management api http-commands
   protocol https
   no shutdown
   !
   vrf MGMT
      no shutdown
!
management ssh
   idle-timeout 0
   no shutdown
   vrf MGT
      no shutdown
!
end
"""
