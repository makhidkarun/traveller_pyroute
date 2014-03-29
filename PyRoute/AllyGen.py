'''
Created on Mar 26, 2014

@author: tjoneslo
'''
from operator import attrgetter
import os

class AllyGen(object):
    '''
    classdocs
    '''


    def __init__(self, galaxy):
        '''
        Constructor
        '''
        self.galaxy = galaxy
        self.noOne = ['Ba']
        self.nonAligned = ['Na', 'Va']
        self.sameAligned = [ ('Im', 'Cs')]
        #self.allyMap = {} # 2d array of star q/r, use tuple to hashcode
        self.borders = {}
        
    def create_borders (self):
        """
            create borders around various allegiances, Algorithm one.
            From the nroute.c generation system. Every world controls a
            two hex radius. Where the allegiances are the same, the area
            of control is contigious. 
        """
        allyMap = {}
        nonAlignedCounter = 9999

        for star in self.galaxy.stars.nodes_iter():
            alg = star.alg
            
            # Skip the non-entity worlds
            if alg in self.noOne:
                continue;
            # Collapse non-aligned into each their own 
            if alg in self.nonAligned:
                alg = nonAlignedCounter
                nonAlignedCounter -= 1
            # Collapse same Aligned into one
            for sameAlg in self.sameAligned:
                if alg in sameAlg:
                    alg = sameAlg[0]
            allyMap[(star.q, star.r)] = alg

        #self._output_map(allyMap, 0)
        
        allyMap = self.step_map(allyMap)
        #self._output_map(allyMap, 1)

        allyMap = self.step_map(allyMap)
        #self._output_map(allyMap, 2)
                        
        for q,r in allyMap.iterkeys():
            if self.set_border(allyMap, q, r, 2): # up
                qn,rn = self._get_neighbor(q, r, 2)
                self.borders[(qn,rn)] = self.borders.setdefault((qn,rn), 0) | 1
            if self.set_border(allyMap, q, r, 5): # down
                self.borders[(q,r)] = self.borders.setdefault((q,r), 0) | 1
            if self.set_border(allyMap, q, r, 1): # upper right
                qn,rn = self._get_neighbor(q, r, 1)
                if q & 1:
                    self.borders[(qn,rn)] = self.borders.setdefault((qn,rn), 0) | 2
                else:
                    self.borders[(qn,rn)] = self.borders.setdefault((qn,rn), 0) | 4
            if self.set_border(allyMap, q, r, 3): # upper left
                if q & 1:
                    self.borders[(q,r)] = self.borders.setdefault((q,r), 0) | 2
                else:
                    self.borders[(q,r-1)] = self.borders.setdefault((q,r-1), 0) | 4
            if self.set_border(allyMap, q, r, 0): # down right
                qn,rn = self._get_neighbor(q, r, 0)
                if q & 1:
                    self.borders[(q+1,r-1)] = self.borders.setdefault((q+1,r-1), 0) | 4
                else:
                    self.borders[(qn,rn)] = self.borders.setdefault((qn,rn), 0) | 2
            if self.set_border(allyMap, q, r, 4): # down left
                if q & 1:
                    self.borders[(q,r)] = self.borders.setdefault((q,r), 0) | 4
                else:
                    self.borders[(q,r)] = self.borders.setdefault((q,r), 0) | 2

    def set_border (self, allyMap, q, r, direction):
        qn, rn = self._get_neighbor(q, r, direction)
        if allyMap[(q,r)] != allyMap.get((qn,rn), None):
            return True
        return False

    def _get_neighbor (self, q, r, direction):
        neighbors = [
           [+1,  0], [+1, -1], [ 0, -1],
           [-1,  0], [-1, +1], [ 0, +1]
        ]
        d = neighbors[direction]
        return (q + d[0], r + d[1])
    
    def step_map(self, allyMap):
        newMap = {}
        for q,r in allyMap.iterkeys():
            newMap[(q,r)] = allyMap[(q,r)]
            for direction in xrange(6):
                qn,rn = self._get_neighbor(q, r, direction)
                if not allyMap.get((qn,rn), False):
                    newMap[(qn,rn)] = allyMap[(q,r)]
        return newMap

    def _output_map(self, allyMap, stage):
        path = os.path.join (self.galaxy.output_path, 'allyMap%s.txt' % stage)
        with open(path, "wb") as f:
            for key, value in allyMap.iteritems():
                f.write("{}-{}: border: {}\n".format(key[0],key[1], value))
        
    def are_allies(self, alg1, alg2):
        if alg1 in self.noOne or alg2 in self.noOne:
            return False
        if alg1 in self.nonAligned or alg2 in self.nonAligned:
            return False
        if alg1 == alg2:
            return True
        
        for sameAlg in self.sameAligned:
            if alg1 in sameAlg and alg2 in sameAlg:
                return True
        
        return False
    
              
    def create_ally_map(self):
        # Sort stars by:
        # Better Port, Higher TL, Higher Population
        stars = [star for star in self.galaxy.stars.node_iter()]
        stars = sorted(stars, key=attrgetter('popCode'), reverse=True)
        stars = sorted(stars, key=attrgetter('tl'), reverse=True)
        stars = sorted(stars, key=attrgetter('port'))

        # Mark the map with all the stars        
        for star in stars:
            alg = star.alg
            # Collapse non-aligned into one value
            if alg in self.nonAligned:
                alg = self.nonAligned[0]
            # Collapse same Aligned into one
            for sameAlg in self.sameAligned:
                if alg in sameAlg:
                    alg = sameAlg[0]
            self.allyMap [(star.q, star.r)] = alg

        for star in stars:
            if star.port in ['E', 'X']: continue
            #foreach my $dist (1..index("DCBA",$Port{$c.$r})+$Fudge)
            for dist in xrange (['D','C','B','A'].index(star.port)+1):
                pass
                

    
