# -*- coding: utf-8 -*-
"""Tentative implementation of Raft consensus algorithm
"""

from __future__ import print_function
from twisted.internet import protocol
from twisted.internet import reactor


CONFIG = {
    'no1': {
        'address': 'localhost',
        'port': 7000,
    },
    'no2': {
        'address': 'localhost',
        'port': 7001,
    },
}


class State:
    FOLLOWER = 0
    CANDIDATE = 1
    LEADER = 2


class Node(object):
    def __init__(self, name, config):
        self.name = name
        self.state = State.FOLLOWER
        self.config = config
        self.peers = []

    def __repr__(self):
        return '%s(name=%s, state=%s, peers=%r)' % (
            self.__class__.__name__, self.name, self.state, self.peers
        )


class RaftNodeInputProtocol(protocol.Protocol):
    """Incoming connections"""
    def connectionMade(self):
        print('Connected to: %s' % (self.transport.getPeer()))


class RaftNodeFactory(protocol.Factory):
    protocol = RaftNodeInputProtocol

    def __init__(self, myself):
        self.myself = myself


class RaftNodeOutputProtocol(protocol.Protocol):
    """Outgoing connections"""
    def connectionMade(self):
        print('Connected to: %s' % (self.transport.getPeer()))
        self.factory.addPeer(self)
        print(self.factory.myself)


class RaftNodeClientFactory(protocol.ReconnectingClientFactory):
    protocol = RaftNodeOutputProtocol

    def __init__(self, myself):
        self.myself = myself
        self.noisy = True

    def addPeer(self, protocol):
        self.myself.peers.append(protocol)


def start(args):
    config = CONFIG[args.node]

    myself = Node(args.node, config)

    print('Listening on port %d' % config['port'])
    reactor.listenTCP(config['port'], RaftNodeFactory(myself))

    for node, cfg in CONFIG.items():
        if node != args.node:
            print('Connecting to: {node} ({address}:{port})'.format(node=node,
                                                                    **cfg))
            reactor.connectTCP(cfg['address'], cfg['port'],
                               RaftNodeClientFactory(myself), timeout=10)
    reactor.run()


if '__main__' == __name__:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('node', help='Node name',
                        choices=CONFIG.keys())

    args = parser.parse_args()
    start(args)
