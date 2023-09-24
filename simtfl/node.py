from .message import Ping, Pong
from .util import skip


class PassiveNode:
    """
    A node that sends no messages and does nothing with received messages.
    This class is intended to be subclassed.
    """
    def __init__(self, ident, env, network):
        """
        Constructs a PassiveNode with the given simpy Environment and network.
        """
        self.ident = ident
        self.env = env
        self.network = network

    def __str__(self):
        return f"{self.ident:2d}: {self.__class__.__name__}"

    def send(self, target, message):
        """
        (process) This method can be overridden to intercept messages being sent
        by this node. It should typically call `self.network.send`.
        """
        return self.network.send(self.ident, target, message)

    def receive(self, sender, message):
        """
        (process) This method can be overridden to intercept messages being received
        by this node. It should typically call `self.handle`.
        """
        return self.handle(sender, message)

    def handle(self, message, sender):
        """
        (process) Handles a message by doing nothing. Note that the handling of
        each message, and the `run` method, are in separate simpy processes. That
        is, yielding here will not block other incoming messages.
        """
        return skip()

    def run(self):
        """
        (process) Runs by doing nothing.
        """
        return skip()


class PingNode(PassiveNode):
    """
    A node that sends pings.
    """
    def run(self):
        """
        (process) Sends a Ping message to every node.
        """
        for i in range(self.network.num_nodes()):
            yield from self.send(i, Ping(i))
            yield self.env.timeout(3)


class PongNode(PassiveNode):
    """
    A node that responds to pings.
    """
    def handle(self, sender, message):
        """
        (process) Handles a Ping message by sending back a Pong message with the same payload.
        """
        if isinstance(message, Ping):
            yield self.env.timeout(5)
            yield from self.send(sender, Pong(message.payload))
        else:
            yield from super().handle(sender, message)