# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/


class Signal_information:
    def __init__(self, signal_power: float, path: list[str]):
        self.signal_power = signal_power
        self.noise_power = 0.0
        self.latency = 0.0
        self.path = path


class Node:
    def __init__(self, node_dict: dict):
        self.label = node_dict['label']  # string
        self.position = tuple(node_dict['position'])  # (float, float)
        self.connected_nodes = node_dict['connected_nodes']  # list[string]
        self.successive = {}  # dict[Line]

    def propagate(self, signal_information):
        # Remove the current node from the signal path
        if signal_information.path:
            signal_information.path.pop(0)

        # If there are still nodes left to visit
        if signal_information.path:
            next_node = signal_information.path[0]
            line = self.successive[self.label + next_node]

            # Propagate signal information to the next line
            line.propagate(signal_information)