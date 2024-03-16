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

        # spin through nodes in bulk, propagating weights upwards
        active_weights = weights[active_nodes]
        while 0 < len(active_nodes):
            #  Directly iterating in python worked out faster than using nditer
            for index in range(len(active_nodes)):
                sizes[active_nodes[index]] += active_weights[index]
            keep = tree[active_nodes] != LandmarkAvoidHelper.TREE_ROOT
            active_nodes = active_nodes[keep]
            active_weights = active_weights[keep]
            active_nodes = tree[active_nodes]  # Move up to immediate parents

        active_nodes = np.array(list(landmarks))
        while 0 < len(active_nodes):
            sizes[active_nodes] = 0
            keep = tree[active_nodes] != LandmarkAvoidHelper.TREE_ROOT
            active_nodes = active_nodes[keep]
            active_nodes = tree[active_nodes]

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
