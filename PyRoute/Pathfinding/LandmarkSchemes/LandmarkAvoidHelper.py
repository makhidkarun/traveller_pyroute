"""
Created on Mar 06, 2024

@author: CyberiaResurrection
"""
import numpy as np


class LandmarkAvoidHelper:

    TREE_ROOT = -1
    TREE_NONE = -100

    @staticmethod
    def calc_weights(distances, lobound):
        return distances - lobound

    @staticmethod
    def calc_sizes(weights, tree, landmarks):
        active_nodes = np.array(range(len(weights)))
        sizes = np.zeros(len(weights))
        # filter out nodes who aren't part of a tree
        keep = tree[active_nodes] != LandmarkAvoidHelper.TREE_NONE
        active_nodes = active_nodes[keep]

        # spin through each node, propagating weights upwards
        for rawnode in active_nodes:
            node = rawnode
            # Add node's weight to its own size
            parent = tree[node]
            ballast = weights[node]
            sizes[node] += ballast
            while LandmarkAvoidHelper.TREE_ROOT != parent:  # If node is not tree root, propagate its weights upwards
                node = parent
                parent = tree[node]
                sizes[node] += ballast

        # spin thru landmarks, propagating their zero weights upwards
        for rawnode in landmarks:
            node = rawnode
            sizes[node] = 0
            parent = tree[node]
            while LandmarkAvoidHelper.TREE_ROOT != parent:  # If node is not tree root, propagate its weights upwards
                node = parent
                parent = tree[node]
                sizes[node] = 0

        return sizes

    @staticmethod
    def traverse_sizes(sizes, rootnode, tree):
        active_nodes = np.array(range(len(sizes)))
        if LandmarkAvoidHelper.TREE_ROOT != tree[rootnode]:
            raise AssertionError("Selected root node " + str(rootnode) + " not marked as a tree root")
        choice = active_nodes[np.argmax(sizes)]
        kidvec = np.where(choice == tree)
        kidsizes = sizes[kidvec]
        maxkid = np.argmax(kidsizes)
        while 0 < len(kidsizes):
            choice = active_nodes[kidvec][maxkid]
            kidvec = np.where(choice == tree)
            kidsizes = sizes[kidvec]
            if 0 < len(kidsizes):
                maxkid = np.argmax(kidsizes)

        return choice
