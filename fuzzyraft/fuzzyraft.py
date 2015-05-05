# -*- coding: utf-8 -*-


class State:
    FOLLOWER = 0
    CANDIDATE = 1
    LEADER = 2


class Node(object):
    def __init__(self):
        self.state = State.FOLLOWER
