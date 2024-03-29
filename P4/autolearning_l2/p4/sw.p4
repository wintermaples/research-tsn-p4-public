#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x0800;
const bit<16> TYPE_802_1_Q = 0x8100;

#define CPU_PORT 255

////////// HEADERS //////////

typedef bit<9> egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ipv4Addr_t;
typedef bit<16> mcast_grp_t;

@controller_header("packet_in")
header packet_in_header_t {
    bit<9> ingress_port;
    bit<7> _pad;
}

@controller_header("packet_out")
header packet_out_header_t {
        bit<9> egress_port;
        bit<9> src_ingress_port;
        bit<16> mcast_grp;
        bit<6> _pad;
}

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16> etherType;
}

header ipv4_t {
    bit<4> version;
    bit<4> ihl;
    bit<8> diffserv;
    bit<16> totalLen;
    bit<16> identification;
    bit<3> flags;
    bit<13> flagOffset;
    bit<8> ttl;
    bit<8> protocol;
    bit<16> hdrChecksum;
    ipv4Addr_t srcAddr;
    ipv4Addr_t dstAddr;
}

header vlan_t {
    bit<3> pcp;
    bit<1> dei;
    bit<12> id;
    bit<16> etherType;
}

struct metadata {

}

struct headers {
    packet_in_header_t packet_in;
    packet_out_header_t packet_out;
    ethernet_t ethernet;
    vlan_t vlan;
    ipv4_t ipv4;
}

////////// PARSERS //////////

parser MyParser(
    packet_in packet,
    out headers hdr,
    inout metadata meta,
    inout standard_metadata_t standard_metadata
) {
    state start {
        transition select(standard_metadata.ingress_port) {
            CPU_PORT: parse_packet_out;
            default: parse_ethernet;
        }
    }

    state parse_packet_out {
        packet.extract(hdr.packet_out);
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4;
            TYPE_802_1_Q: parse_vlan;
            default: accept;
        }
    }

    state parse_vlan {
        packet.extract(hdr.vlan);
        transition select(hdr.vlan.etherType) {
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition accept;
    }
}

////////// Checksum Verification //////////

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {}
}

////////// Ingress //////////

control MyIngress(
    inout headers hdr,
    inout metadata meta,
    inout standard_metadata_t standard_metadata
) {
    action send_to_controller() {
        standard_metadata.egress_spec = CPU_PORT;
        hdr.packet_in.setValid();
        hdr.packet_in.ingress_port = standard_metadata.ingress_port;
    }

    action forward(egressSpec_t port) {
        standard_metadata.egress_spec = port;
    }

    action drop() {
        mark_to_drop(standard_metadata);
    }

    table ether_addr_table {
        key = {
            hdr.ethernet.srcAddr: exact;
            hdr.ethernet.dstAddr: exact;
        }
        actions = {
            send_to_controller;
            forward;
            drop;
        }
        size = 1024;
        default_action = send_to_controller;
    }

    apply {
        if (hdr.packet_out.isValid()) {
            if (hdr.packet_out.mcast_grp != 0) {
                standard_metadata.mcast_grp = hdr.packet_out.mcast_grp;
                standard_metadata.egress_spec = hdr.packet_out.egress_port;
            } else {
                standard_metadata.egress_spec = hdr.packet_out.egress_port;
            }
            if (hdr.packet_out.src_ingress_port != 0) {
                standard_metadata.ingress_port = hdr.packet_out.src_ingress_port;
            }
            hdr.packet_out.setInvalid();
        } else {
            // Set priority queue based on PCP if 802.1Q is valid
            if (hdr.vlan.isValid()) {
                standard_metadata.priority = hdr.vlan.pcp;
            }

            if (hdr.ethernet.isValid()) {
                ether_addr_table.apply();
            }
        }
    }
}

////////// Egress //////////

control MyEgress(
    inout headers hdr,
    inout metadata meta,
    inout standard_metadata_t standard_metadata
) {
    action drop() {
        mark_to_drop(standard_metadata);
    }

    apply {
        // Prune multicast packet to ingress port to preventing loop
        if (standard_metadata.egress_port == standard_metadata.ingress_port) {
            drop();
        }
    }
}

////////// Checksum Computation //////////

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
        update_checksum(
        hdr.ipv4.isValid(),
            { hdr.ipv4.version,
              hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.flagOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

////////// Deparser //////////

control MyDeparser(
    packet_out packet,
    in headers hdr
) {
    apply {
        packet.emit(hdr.packet_in);
        packet.emit(hdr.packet_out);
        packet.emit(hdr.ethernet);
        packet.emit(hdr.vlan);
        packet.emit(hdr.ipv4);
    }
}

////////// Switch //////////

V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;