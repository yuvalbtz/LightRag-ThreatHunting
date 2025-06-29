from scapy.packet import Packet

from . import constants
from .features.context import PacketDirection, get_packet_flow_key
from .features.flag_count import FlagCount
from .features.flow_bytes import FlowBytes
from .features.packet_count import PacketCount
from .features.packet_length import PacketLength
from .features.packet_time import PacketTime
from .utils import get_statistics


class Flow:
    """This class summarizes the values of the features of the network flows"""

    def __init__(self, packet: Packet, direction: PacketDirection):
        """This method initializes an object from the Flow class.

        Args:
            packet (Any): A packet from the network.
            direction (Enum): The direction the packet is going ove the wire.
        """

        (
            self.src_ip,
            self.dest_ip,
            self.src_port,
            self.dest_port,
        ) = get_packet_flow_key(packet, direction)

        # Initialize flow properties with the first packet
        self.packets = [(packet, direction)]  # Add the first packet
        self.flow_interarrival_time = []
        self.start_timestamp = packet.time
        self.latest_timestamp = packet.time  # Initialize latest_timestamp too
        self.protocol = packet.proto

        # Initialize window sizes
        self.init_window_size = {PacketDirection.FORWARD: 0, PacketDirection.REVERSE: 0}
        if "TCP" in packet:
            # Set initial window size based on the first packet's direction
            self.init_window_size[direction] = packet["TCP"].window

        # Initialize active/idle tracking
        self.start_active = packet.time
        self.last_active = 0
        self.active = []
        self.idle = []

        self.forward_bulk_last_timestamp = 0
        self.forward_bulk_start_tmp = 0
        self.forward_bulk_count = 0
        self.forward_bulk_count_tmp = 0
        self.forward_bulk_duration = 0
        self.forward_bulk_packet_count = 0
        self.forward_bulk_size = 0
        self.forward_bulk_size_tmp = 0
        self.backward_bulk_last_timestamp = 0
        self.backward_bulk_start_tmp = 0
        self.backward_bulk_count = 0
        self.backward_bulk_count_tmp = 0
        self.backward_bulk_duration = 0
        self.backward_bulk_packet_count = 0
        self.backward_bulk_size = 0
        self.backward_bulk_size_tmp = 0

    def get_data(self, include_fields=None) -> dict:
        """This method obtains the values of the features extracted from each flow.

        Note:
            Only some of the network data plays well together in this list.
            Time-to-live values, window values, and flags cause the data to
            separate out too much.

        Returns:
           list: returns a List of values to be outputted into a csv file.

        """

        flow_bytes = FlowBytes(self)
        flag_count = FlagCount(self)
        packet_count = PacketCount(self)
        packet_length = PacketLength(self)
        packet_time = PacketTime(self)
        flow_iat = get_statistics(self.flow_interarrival_time)
        forward_iat = get_statistics(
            packet_time.get_packet_iat(PacketDirection.FORWARD)
        )
        backward_iat = get_statistics(
            packet_time.get_packet_iat(PacketDirection.REVERSE)
        )
        active_stat = get_statistics(self.active)
        idle_stat = get_statistics(self.idle)

        data = {
            # Basic IP information
            "Source IP": self.src_ip,
            "Destination IP": self.dest_ip,
            "Source Port": self.src_port,
            "Destination Port": self.dest_port,
            "Protocol": self.protocol,
            # Basic information from packet times
            "Timestamp": packet_time.get_timestamp(),
            "Flow Duration": packet_time.get_duration(),
            "Flow Bytes/s": flow_bytes.get_rate(),
            "Flow Packets/s": packet_count.get_rate(),
            "Fwd Packets/s": packet_count.get_rate(PacketDirection.FORWARD),
            "Bwd Packets/s": packet_count.get_rate(PacketDirection.REVERSE),
            # Count total packets by direction
            "Total Fwd Packets": packet_count.get_total(PacketDirection.FORWARD),
            "Total Backward Packets": packet_count.get_total(PacketDirection.REVERSE),
            # Statistical info obtained from Packet lengths
            "Total Length of Fwd Packets": packet_length.get_total(
                PacketDirection.FORWARD
            ),
            "Total Length of Bwd Packets": packet_length.get_total(
                PacketDirection.REVERSE
            ),
            "Fwd Packet Length Max": packet_length.get_max(PacketDirection.FORWARD),
            "Fwd Packet Length Min": packet_length.get_min(PacketDirection.FORWARD),
            "Fwd Packet Length Mean": packet_length.get_mean(PacketDirection.FORWARD),
            "Fwd Packet Length Std": packet_length.get_std(PacketDirection.FORWARD),
            "Bwd Packet Length Max": packet_length.get_max(PacketDirection.REVERSE),
            "Bwd Packet Length Min": packet_length.get_min(PacketDirection.REVERSE),
            "Bwd Packet Length Mean": packet_length.get_mean(PacketDirection.REVERSE),
            "Bwd Packet Length Std": packet_length.get_std(PacketDirection.REVERSE),
            "Max Packet Length": packet_length.get_max(),
            "Min Packet Length": packet_length.get_min(),
            "Packet Length Mean": packet_length.get_mean(),
            "Packet Length Std": packet_length.get_std(),
            "Packet Length Variance": packet_length.get_var(),
            "Fwd Header Length": flow_bytes.get_forward_header_bytes(),
            "Bwd Header Length": flow_bytes.get_reverse_header_bytes(),
            "min_seg_size_forward": flow_bytes.get_min_forward_header_bytes(),
            "act_data_pkt_fwd": packet_count.has_payload(PacketDirection.FORWARD),
            # Flows Interarrival Time
            "Flow IAT Mean": flow_iat["mean"],
            "Flow IAT Max": flow_iat["max"],
            "Flow IAT Min": flow_iat["min"],
            "Flow IAT Std": flow_iat["std"],
            # Forward inter-arrival times
            "Fwd IAT Total": forward_iat["total"],
            "Fwd IAT Max": forward_iat["max"],
            "Fwd IAT Min": forward_iat["min"],
            "Fwd IAT Mean": forward_iat["mean"],
            "Fwd IAT Std": forward_iat["std"],
            # Backward inter-arrival times
            "Bwd IAT Total": backward_iat["total"],
            "Bwd IAT Max": backward_iat["max"],
            "Bwd IAT Min": backward_iat["min"],
            "Bwd IAT Mean": backward_iat["mean"],
            "Bwd IAT Std": backward_iat["std"],
            # Flags statistics
            "Fwd PSH Flags": flag_count.count("PSH", PacketDirection.FORWARD),
            "Bwd PSH Flags": flag_count.count("PSH", PacketDirection.REVERSE),
            "Fwd URG Flags": flag_count.count("URG", PacketDirection.FORWARD),
            "Bwd URG Flags": flag_count.count("URG", PacketDirection.REVERSE),
            "FIN Flag Count": flag_count.count("FIN"),
            "SYN Flag Count": flag_count.count("SYN"),
            "RST Flag Count": flag_count.count("RST"),
            "PSH Flag Count": flag_count.count("PSH"),
            "ACK Flag Count": flag_count.count("ACK"),
            "URG Flag Count": flag_count.count("URG"),
            "ECE Flag Count": flag_count.count("ECE"),
            "CWE Flag Count": flag_count.count(
                "URG", PacketDirection.FORWARD
            ),  # Alias for cwr_flag_count
            # Response Time
            "Down/Up Ratio": packet_count.get_down_up_ratio(),
            "Average Packet Size": packet_length.get_avg(),
            # Window sizes
            "Init_Win_bytes_forward": self.init_window_size[PacketDirection.FORWARD],
            "Init_Win_bytes_backward": self.init_window_size[PacketDirection.REVERSE],
            # Active/Idle periods
            "Active Max": active_stat["max"],
            "Active Min": active_stat["min"],
            "Active Mean": active_stat["mean"],
            "Active Std": active_stat["std"],
            "Idle Max": idle_stat["max"],
            "Idle Min": idle_stat["min"],
            "Idle Mean": idle_stat["mean"],
            "Idle Std": idle_stat["std"],
            # Bulk transfer statistics
            "Fwd Avg Bytes/Bulk": flow_bytes.get_bytes_per_bulk(
                PacketDirection.FORWARD
            ),
            "Fwd Avg Packets/Bulk": flow_bytes.get_packets_per_bulk(
                PacketDirection.FORWARD
            ),
            "Bwd Avg Bytes/Bulk": flow_bytes.get_bytes_per_bulk(
                PacketDirection.REVERSE
            ),
            "Bwd Avg Packets/Bulk": flow_bytes.get_packets_per_bulk(
                PacketDirection.REVERSE
            ),
            "Fwd Avg Bulk Rate": flow_bytes.get_bulk_rate(PacketDirection.FORWARD),
            "Bwd Avg Bulk Rate": flow_bytes.get_bulk_rate(PacketDirection.REVERSE),
            # Segment sizes
            "Avg Fwd Segment Size": packet_length.get_mean(PacketDirection.FORWARD),
            "Avg Bwd Segment Size": packet_length.get_mean(PacketDirection.REVERSE),
            # Subflow statistics
            "Subflow Fwd Packets": packet_count.get_total(PacketDirection.FORWARD),
            "Subflow Bwd Packets": packet_count.get_total(PacketDirection.REVERSE),
            "Subflow Fwd Bytes": packet_length.get_total(PacketDirection.FORWARD),
            "Subflow Bwd Bytes": packet_length.get_total(PacketDirection.REVERSE),
        }

        if include_fields is not None:
            data = {k: v for k, v in data.items() if k in include_fields}

        return data

    def add_packet(self, packet: Packet, direction: PacketDirection) -> None:
        """Adds a packet to the current list of packets.

        Args:
            packet: Packet to be added to a flow
            direction: The direction the packet is going in that flow

        """
        self.packets.append((packet, direction))

        # Calculate interarrival time using the previous latest_timestamp
        # This check prevents adding a 0 IAT for the very first packet added after init
        if len(self.packets) > 1:
            self.flow_interarrival_time.append(packet.time - self.latest_timestamp)

        # Update latest timestamp
        self.latest_timestamp = max(packet.time, self.latest_timestamp)

        # Update flow bulk and subflow stats
        self.update_flow_bulk(packet, direction)
        self.update_subflow(packet)

        # Update initial window size if not already set for this direction
        if "TCP" in packet and self.init_window_size[direction] == 0:
            self.init_window_size[direction] = packet["TCP"].window

        # Note: start_timestamp and protocol are set in __init__

    def update_subflow(self, packet: Packet):
        """Update subflow

        Args:
            packet: Packet to be parse as subflow

        """
        last_timestamp = (
            self.latest_timestamp if self.latest_timestamp != 0 else packet.time
        )
        if (packet.time - last_timestamp) > constants.CLUMP_TIMEOUT:
            self.update_active_idle(packet.time - last_timestamp)

    def update_active_idle(self, current_time):
        """Adds a packet to the current list of packets.

        Args:
            packet: Packet to be update active time

        """
        if (current_time - self.last_active) > constants.ACTIVE_TIMEOUT:
            duration = abs(self.last_active - self.start_active)
            if duration > 0:
                self.active.append(duration)
            self.idle.append(current_time - self.last_active)
            self.start_active = current_time
            self.last_active = current_time
        else:
            self.last_active = current_time

    def update_flow_bulk(self, packet: Packet, direction: PacketDirection):
        """Update bulk flow

        Args:
            packet: Packet to be parse as bulk

        """
        payload_size = len(PacketCount.get_payload(packet))
        if payload_size == 0:
            return
        if direction == PacketDirection.FORWARD:
            if self.backward_bulk_last_timestamp > self.forward_bulk_start_tmp:
                self.forward_bulk_start_tmp = 0
            if self.forward_bulk_start_tmp == 0:
                self.forward_bulk_start_tmp = packet.time
                self.forward_bulk_last_timestamp = packet.time
                self.forward_bulk_count_tmp = 1
                self.forward_bulk_size_tmp = payload_size
            else:
                if (
                    packet.time - self.forward_bulk_last_timestamp
                ) > constants.CLUMP_TIMEOUT:
                    self.forward_bulk_start_tmp = packet.time
                    self.forward_bulk_last_timestamp = packet.time
                    self.forward_bulk_count_tmp = 1
                    self.forward_bulk_size_tmp = payload_size
                else:  # Add to bulk
                    self.forward_bulk_count_tmp += 1
                    self.forward_bulk_size_tmp += payload_size
                    if self.forward_bulk_count_tmp == constants.BULK_BOUND:
                        self.forward_bulk_count += 1
                        self.forward_bulk_packet_count += self.forward_bulk_count_tmp
                        self.forward_bulk_size += self.forward_bulk_size_tmp
                        self.forward_bulk_duration += (
                            packet.time - self.forward_bulk_start_tmp
                        )
                    elif self.forward_bulk_count_tmp > constants.BULK_BOUND:
                        self.forward_bulk_packet_count += 1
                        self.forward_bulk_size += payload_size
                        self.forward_bulk_duration += (
                            packet.time - self.forward_bulk_last_timestamp
                        )
                    self.forward_bulk_last_timestamp = packet.time
        else:
            if self.forward_bulk_last_timestamp > self.backward_bulk_start_tmp:
                self.backward_bulk_start_tmp = 0
            if self.backward_bulk_start_tmp == 0:
                self.backward_bulk_start_tmp = packet.time
                self.backward_bulk_last_timestamp = packet.time
                self.backward_bulk_count_tmp = 1
                self.backward_bulk_size_tmp = payload_size
            else:
                if (
                    packet.time - self.backward_bulk_last_timestamp
                ) > constants.CLUMP_TIMEOUT:
                    self.backward_bulk_start_tmp = packet.time
                    self.backward_bulk_last_timestamp = packet.time
                    self.backward_bulk_count_tmp = 1
                    self.backward_bulk_size_tmp = payload_size
                else:  # Add to bulk
                    self.backward_bulk_count_tmp += 1
                    self.backward_bulk_size_tmp += payload_size
                    if self.backward_bulk_count_tmp == constants.BULK_BOUND:
                        self.backward_bulk_count += 1
                        self.backward_bulk_packet_count += self.backward_bulk_count_tmp
                        self.backward_bulk_size += self.backward_bulk_size_tmp
                        self.backward_bulk_duration += (
                            packet.time - self.backward_bulk_start_tmp
                        )
                    elif self.backward_bulk_count_tmp > constants.BULK_BOUND:
                        self.backward_bulk_packet_count += 1
                        self.backward_bulk_size += payload_size
                        self.backward_bulk_duration += (
                            packet.time - self.backward_bulk_last_timestamp
                        )
                    self.backward_bulk_last_timestamp = packet.time

    @property
    def duration(self):
        return self.latest_timestamp - self.start_timestamp
