'''
Created on Mar 2, 2014

@author: tjoneslo
'''
import logging

class Galaxy(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.logger = logging.getLogger(__name__)

        
    def read_sectors (self, sectors):
        
        