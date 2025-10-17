from __future__ import annotations

from typing import Dict, List
import json
import math


# ----------------------------
# 1) Signal_information
# ----------------------------
class Signal_information:
    def __init__(self, signal_power: float, path: List[str]):
        self.signal_power = signal_power
        self.noise_power = 0.0
        self.latency = 0.0
        self.path = list(path)  # copy for safety

    # --- increment helpers per spec ---
    def update_signal_power(self, increment: float) -> None:
        self.signal_power += increment

    def update_noise_power(self, increment: float) -> None:
        self.noise_power += increment

    def update_latency(self, increment: float) -> None:
        self.latency += increment

    def update_path(self) -> None:
        if self.path:
            self.path.pop(0)


# ----------------------------
# 2) Node
# ----------------------------
class Node:
    def __init__(self, node_dict: dict):
        self.label: str = node_dict["label"]
        self.position = tuple(node_dict["position"])          # (float, float)
        self.connected_nodes: List[str] = list(node_dict["connected_nodes"])
        self.successive: Dict[str, "Line"] = {}               # filled by Network.connect()

    def propagate(self, signal_information: Signal_information) -> None:
        # We are at this node → consume it from the path
        signal_information.update_path()

        # If there is a next node, forward the signal to the proper line
        if signal_information.path:
            next_node = signal_information.path[0]
            line_key = self.label + next_node                 # e.g., 'AB'
            line = self.successive[line_key]
            line.propagate(signal_information)


# ----------------------------
# 3) Line
# ----------------------------
class Line:
    def __init__(self, label: str, length: float):
        self.label = label
        self.length = float(length)
        self.successive: Dict[str, Node] = {}                 # next node after this line

    def latency_generation(self) -> float:
        # Light speed in fiber ≈ 2/3 c
        c = 3e8
        v = (2.0 / 3.0) * c
        return self.length / v

    def noise_generation(self, signal_power: float) -> float:
        # Given in the spec
        return 1e-9 * signal_power * self.length

    def propagate(self, signal_information: Signal_information) -> None:
        # Update latency and noise (increments)
        signal_information.update_latency(self.latency_generation())
        signal_information.update_noise_power(
            self.noise_generation(signal_information.signal_power)
        )

        # Hand off to the next node in the path
        if signal_information.path:
            next_node_label = signal_information.path[0]
            next_node = self.successive[next_node_label]
            next_node.propagate(signal_information)


# ----------------------------
# 4) Network
# ----------------------------
class Network:
    def __init__(self, json_path: str = "nodes.json"):
        """
        Build Node objects from a JSON topology file.
        JSON format:
        {
          "A": {"label":"A", "position":[0,0], "connected_nodes":["B","C"]},
          ...
        }
        """
        self.nodes: Dict[str, Node] = {}
        self.lines: Dict[str, Line] = {}

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for label, nd in data.items():
            nd = dict(nd)
            nd.setdefault("label", label)
            self.nodes[label] = Node(nd)

    def connect(self) -> None:
        """
        Create directed Line objects for every adjacency and wire up 'successive'.
        Line length = Euclidean distance between node positions.
        """
        # Create all lines
        for a_label, node_a in self.nodes.items():
            ax, ay = node_a.position
            for b_label in node_a.connected_nodes:
                bx, by = self.nodes[b_label].position
                length = math.hypot(bx - ax, by - ay)
                ab = a_label + b_label
                if ab not in self.lines:
                    self.lines[ab] = Line(ab, length)

        # Connect node -> line and line -> next node
        for a_label, node_a in self.nodes.items():
            for b_label in node_a.connected_nodes:
                ab = a_label + b_label
                line_ab = self.lines[ab]
                node_a.successive[ab] = line_ab
                line_ab.successive[b_label] = self.nodes[b_label]

    def find_paths(self, start: str, end: str) -> List[List[str]]:
        """Return all simple paths (no node repeated) from start to end."""
        if start not in self.nodes or end not in self.nodes:
            return []
        paths: List[List[str]] = []

        def dfs(curr: str, path: List[str]):
            if curr == end:
                paths.append(path[:])
                return
            for nxt in self.nodes[curr].connected_nodes:
                if nxt not in path:
                    dfs(nxt, path + [nxt])

        dfs(start, [start])
        return paths

    def propagate(self, signal_information: Signal_information) -> Signal_information:
        """Start propagation from the first node in the signal path."""
        if not signal_information.path:
            return signal_information
        start_label = signal_information.path[0]
        self.nodes[start_label].propagate(signal_information)
        return signal_information

    def draw(self) -> None:
        """Draw the network (optional)."""
        import matplotlib.pyplot as plt  # local import so matplotlib is optional

        fig, ax = plt.subplots()

        # Lines
        for lbl, line in self.lines.items():
            a, b = lbl[0], lbl[1]
            x1, y1 = self.nodes[a].position
            x2, y2 = self.nodes[b].position
            ax.plot([x1, x2], [y1, y2])

        # Nodes
        for lbl, node in self.nodes.items():
            x, y = node.position
            ax.scatter([x], [y])
            ax.text(x, y, f" {lbl}", va="center", ha="left")

        ax.set_aspect("equal")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title("Network")
        plt.show()
