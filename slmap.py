#!/usr/bin/python
# -*- coding: utf-8 -*-

class SLMap:
    def __init__(self, filename):
        self.load(filename)

    def load(self, filename):
        mapfile = open(filename, "r")
        if mapfile.readline() != "SLMap 1\n":
            return False
        headerStage = 0 # No header line parsed yet.
        for line in mapfile:
            if line[0] == "#":
                continue
            elif headerStage == 0:
                self.title = line.strip()
                headerStage += 1 # Now, we know the title of the map
            elif headerStage == 1:
                self.x, self.y = [int(_) for _ in line.strip().split(" ")]
                headerStage = -1 # Now, we know the size of the map
                                 # Header reading done
            else:
                pass
