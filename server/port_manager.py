
class PortManager:
    def __init__(self):
        self.PORT_IN_USE = []

    def update_port_in_use(self, port):
        self.PORT_IN_USE.append(port)

    def is_port_in_use(self, port):
        return port in self.PORT_IN_USE

    def get_port_in_use(self):
        return self.PORT_IN_USE

    def clear_ports(self):
        self.PORT_IN_USE.clear()
