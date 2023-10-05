import abc
import argparse
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from typing import Any, Optional
from p4runtime_sh.context import P4Type
from p4runtime_sh.shell import FwdPipeConfig, MulticastGroupEntry, PacketOut, TableEntry
from p4runtime_sh import shell
import time
import threading
import logging
import sys
import os

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)
sys.stdin = os.fdopen(sys.stdin.fileno(), 'r', buffering=1)

FLOODING_MCAST_GROUP_ID: int = 255


def get_metadata_value(metadata_fields, metadata_name, metadata_field_name) -> Any | None:
    metadata_field_id = None

    controller_packet_metadata = shell.context.get_obj(
        P4Type.controller_packet_metadata, metadata_name)
    if controller_packet_metadata is None:
        return None

    for metadata_field in controller_packet_metadata.metadata:
        if metadata_field.name == metadata_field_name:
            metadata_field_id = metadata_field.id
            break

    if metadata_field_id is None:
        return None

    for metadata_field in metadata_fields:
        if metadata_field.metadata_id == metadata_field_id:
            return metadata_field.value

    return None


class SwitchFeature(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def setup_feature(self) -> threading.Thread:
        """Setup the feature and returns feature thread.

        Returns:
            threading.Thread: A thread to run the feature.
        """
        raise NotImplementedError()


class SwitchFeature_SetMulticastGroup(SwitchFeature):
    def __init__(
        self,
        mcast_group_id: int,
        egress_ports: set[int],
    ) -> None:
        super().__init__()
        self.mcast_group_id = mcast_group_id
        self.egress_ports = egress_ports

    def setup_feature(self) -> threading.Thread:
        mge = MulticastGroupEntry(self.mcast_group_id)
        for egress_port in self.egress_ports:
            mge.add(egress_port)
        mge.insert()

        return threading.Thread(target=lambda: None)


class SwitchFeature_L2AutoLearning(SwitchFeature):
    """A switch feature which implements L2 Auto Learning Switch.

    This class implements L2 Auto Learning Switch.

    Note:
        To include this feature collectly, P4 Program must implements belows.
        - P4 Program must send packets to the controller which is not in routing tables.
        - P4 Program must have controller headers "packet_in", "packet_out".

        ```
            @controller_header("packet_in")
            header packet_in_header_t {
                bit<9> ingress_port;
                bit<7> _pad;
            }

            @controller_header("packet_out")
            header packet_out_header_t {
                    bit<9> egress_port;
                    bit<7> _pad;
                    bit<16> mcast_grp;
            }

            // ...

            headers {
                packet_in_header_t packet_in;
                packet_out_header_t packet_out;
                // ...
            }
        ```

        - P4 Program must parse "packet_out" header if ingress_port == CPU_PORT.
        - P4 Program must set standard_metadata.mcast_grp and invalid "packet_out" header if "packet_out" is valid and packet_out.mcast_grp != 0.
        - P4 Program must emit "packet_in", "packet_out" header.
        - P4 Program must have forward action.
    """

    PACKET_IN_HEADER_NAME = 'packet_in'
    PACKET_IN_HEADER_INGRESS_PORT_NAME = 'ingress_port'

    class L2LearningThread(threading.Thread):

        def __init__(self, group: None = None, target: Callable[..., object] | None = None, name: str | None = None, args: Iterable[Any] = [], kwargs: Mapping[str, Any] | None = None, *, daemon: bool | None = None) -> None:
            super().__init__(group, target, name, args, kwargs, daemon=daemon)
            assert kwargs is not None
            self.table_name = kwargs['table_name']
            self.forward_action_name = kwargs['forward_action_name']

        l2_table: dict[str, int] = {}

        def run(self):
            while True:
                rep = shell.client.get_stream_packet("packet", timeout=None)
                if rep is not None:
                    payload = rep.packet.payload
                    dst_mac: str = f"0x{payload[0:6].hex()}"
                    src_mac: str = f"0x{payload[6:12].hex()}"

                    ingress_port_bytes: bytes | None = get_metadata_value(
                        rep.packet.metadata,
                        SwitchFeature_L2AutoLearning.PACKET_IN_HEADER_NAME,
                        SwitchFeature_L2AutoLearning.PACKET_IN_HEADER_INGRESS_PORT_NAME,
                    )
                    assert ingress_port_bytes is not None
                    ingress_port: int = int(ingress_port_bytes.hex())

                    if src_mac not in self.l2_table:
                        self.l2_table[src_mac] = ingress_port

                    if src_mac in self.l2_table and dst_mac in self.l2_table:
                        te = TableEntry(self.table_name)(
                            action=self.forward_action_name)
                        te.match['hdr.ethernet.srcAddr'] = dst_mac
                        te.match['hdr.ethernet.dstAddr'] = src_mac
                        te.action['port'] = str(self.l2_table[src_mac])
                        te.read(function=lambda e: e.delete())
                        te.insert()

                        te = TableEntry(self.table_name)(
                            action=self.forward_action_name)
                        te.match['hdr.ethernet.srcAddr'] = src_mac
                        te.match['hdr.ethernet.dstAddr'] = dst_mac
                        te.action['port'] = str(self.l2_table[dst_mac])
                        te.read(function=lambda e: e.delete())
                        te.insert()

                        PacketOut(
                            payload=payload,
                            egress_port=str(self.l2_table[dst_mac]),
                        ).send()
                    else:
                        PacketOut(
                            payload=payload,
                            egress_port=str(ingress_port),
                            mcast_grp=str(FLOODING_MCAST_GROUP_ID),
                        ).send()
                        
                    for te in shell.TableEntry(self.table_name).read():
                        print(te)
                    print(ingress_port)
                    print(src_mac)
                    print(dst_mac)
                    print("=" * 20)

                time.sleep(0.1)

    def __init__(self,
                 flooding_mcast_group_id: int,
                 table_name: str,
                 forward_action_name: str,
                 ) -> None:
        super().__init__()
        self.flooding_mcast_group_id = flooding_mcast_group_id
        self.table_name = table_name
        self.forward_action_name = forward_action_name

    def setup_feature(self):
        t = self.L2LearningThread(
            kwargs={
                'table_name': self.table_name,
                'forward_action_name': self.forward_action_name,
            }
        )
        return t


class SwitchController(metaclass=abc.ABCMeta):

    def start_connection(self):
        logging.info(f"Connecting to {self.grpc_addr}")
        shell.setup(
            device_id=self.device_id,
            grpc_addr=self.grpc_addr,
            config=self.config,
            election_id=self.election_id,
            role_name=self.role_name,
            ssl_options=self.ssl_options
        )
        logging.info(f"Connected to {self.grpc_addr}")

    @property
    @abc.abstractmethod
    def switch_name(self) -> str:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def device_id(self) -> int:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def grpc_addr(self) -> str:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def config(self) -> FwdPipeConfig:
        raise NotImplementedError()

    @property
    def election_id(self) -> tuple[int, int]:
        return (1, 0)

    @property
    def role_name(self) -> str | None:
        return None

    @property
    def ssl_options(self):
        return None

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError()


class ExternalConfigSwitchController(SwitchController):
    def __init__(
            self,
            device_id: int,
            grpc_addr: str,
            config: FwdPipeConfig,
            election_id: tuple[int, int] = (1, 0),
            role_name: str | None = None,
            ssl_options=None,
    ) -> None:
        super().__init__()
        self._device_id = device_id
        self._grpc_addr = grpc_addr
        self._config = config
        self._election_id = election_id
        self._role_name = role_name
        self._ssl_options = ssl_options

    @property
    def device_id(self) -> int:
        return self._device_id

    @property
    def grpc_addr(self) -> str:
        return self._grpc_addr

    @property
    def config(self) -> FwdPipeConfig:
        return self._config

    @property
    def election_id(self) -> tuple[int, int]:
        return self._election_id

    @property
    def role_name(self) -> str | None:
        return self._role_name

    @property
    def ssl_options(self):
        return self._ssl_options


class SwitchController_SW001(ExternalConfigSwitchController):

    @property
    def switch_name(self) -> str:
        return "SW001"

    def run(self):
        features: list[SwitchFeature] = [
            SwitchFeature_SetMulticastGroup(
                mcast_group_id=FLOODING_MCAST_GROUP_ID,
                egress_ports={1, 2},
            ),
            SwitchFeature_L2AutoLearning(
                flooding_mcast_group_id=FLOODING_MCAST_GROUP_ID,
                table_name="ether_addr_table",
                forward_action_name="forward",
            ),
        ]

        feature_threads: list[threading.Thread] = []
        for feature in features:
            feature_threads.append(
                feature.setup_feature()
            )

        for feature_thread in feature_threads:
            feature_thread.start()

        for feature_thread in feature_threads:
            feature_thread.join()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("switch_name")
    parser.add_argument("--grpc-addr", required=True)
    parser.add_argument("--config", required=True)

    args = parser.parse_args()
    switch_name: str = args.switch_name
    grpc_addr: str = args.grpc_addr
    config: str = args.config

    switches: list[SwitchController] = [
        SwitchController_SW001(
            device_id=1,
            grpc_addr=grpc_addr,
            config=FwdPipeConfig(*config.split(',')),
        )
    ]

    target_switch: SwitchController | None = next(
        filter(lambda sw: sw.switch_name == switch_name, switches), None
    )

    if target_switch is None:
        logging.error(f"The specified switch {switch_name} is not found.")
        exit(-1)

    target_switch.start_connection()
    target_switch.run()

    # init()
    # sniff_thread = threading.Thread(target=sniff)
    # sniff_thread.start()
    # sniff_thread.join()


if __name__ == '__main__':
    main()
