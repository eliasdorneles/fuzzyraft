# -*- coding: utf-8 -*-
"""Tentative implementation of Raft consensus algorithm
"""

from __future__ import print_function
import json
from twisted.internet import protocol
from twisted.internet import reactor
from collections import namedtuple


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


class JsonDictMixin(object):

    def to_dict(self):
        d = {field: getattr(self, field) for field in self._fields}
        d['type'] = self.__class__.__name__
        return d

    def to_json(self):
        return json.dumps(self.to_dict())


class AppendEntries(namedtuple('AppendEntries',
                               'term leaderId prevLogIndex prevLogTerm entries leaderCommit'),
                    JsonDictMixin):
    pass


class RequestVote(namedtuple('RequestVote', 'term candidateId lastLogIndex lastLogTerm'),
                  JsonDictMixin):
    pass


class Node(object):
    def __init__(self, name, config):
        self.name = name
        self.state = State.FOLLOWER
        self.config = config
        self.peers = []
        self.term = 0
        self.voteCount = 0

    def __repr__(self):
        return '%s(name=%s, state=%s, peers=%r)' % (
            self.__class__.__name__, self.name, self.state, self.peers
        )


class RaftNodeInputProtocol(protocol.Protocol):
    """Incoming connections"""
    def connectionMade(self):
        print('Connected to: %s' % (self.transport.getPeer()))

        election_timeout = 10
        reactor.callLater(election_timeout, self.maybeStartElection)

    def maybeStartElection(self):
        if self.factory.shouldStartElection:
            print('Will start election')
            # TODO: vote for itself and send RequestVote to all peers
        else:
            print('Will NOT start election')

    def dataReceived(self, data):
        message = json.loads(data)
        if message['type'] in ('AppendEntries', 'RequestVote'):
            self.factory.shouldStartElection = False
        else:
            raise ValueError('Unknown message')


class RaftNodeFactory(protocol.Factory):
    protocol = RaftNodeInputProtocol

    def __init__(self, myself):
        self.myself = myself
        self.shouldStartElection = True


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


def get_config_for_peers(myself, CONFIG):
    for node, cfg in CONFIG.items():
        if node != myself.name:
            yield node, cfg


def start(args):
    config = CONFIG[args.node]

    myself = Node(args.node, config)

    print('Listening on port %d' % config['port'])
    reactor.listenTCP(config['port'], RaftNodeFactory(myself))

    for node, cfg in get_config_for_peers(myself, CONFIG):
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
