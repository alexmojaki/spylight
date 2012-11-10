#!/usr/bin/python
# -*- coding: utf-8 -*-

class SLMap:
    # Header parsing stage
    MAP_TITLE, MAP_DIMENSIONS = range(0, 2)
    HEADER_PARSED = -1

    # Body directives
    WALL_DIRECTIVE = range(0, 1)
    NO_DIRECTIVE = -1

    this.wallType = dict()

    def __init__(self, filename):
        self.load(filename)

    def load(self, filename):
        mapfile = open(filename, "r")

        if mapfile.readline() != "SLMap 1\n":
            return False

        headerStage = MAP_TITLE # No header line parsed yet.
        currentDirective = NO_DIRECTIVE # No directive found yet.

        for line in mapfile:
            line = line.strip()
            lineSplit = line.split()

            if line[0] == "#":
                # Comment
                continue

            elif line == "":
                # Empty line
                continue

            elif headerStage == MAP_TITLE:
                # Map title
                self.title = line
                headerStage = MAP_DIMENSIONS # Now, we know the title of the map

            elif headerStage == MAP_DIMENSIONS:
                # Map dimensions
                self.width, self.height = [int(_) for _ in lineSplit]
                self.wallType = [-1] * (self.width * self.height)
                headerStage = HEADER_PARSED # Now, we know the size of the map
                                            # Header reading done

            elif lineSplit[0] == "wa:":
                # Wall directives
                currentDirective = WALL_DIRECTIVE # Wall directive

            # Put other directives here!

            elif currentDirective == WALL_DIRECTIVE:
                x, y, t = lineSplit[0], lineSplit[1], lineSplit[2]
                self.wallType[y * self.width + x] = t

    def getWallType(x, y):
        return self.wallType[y * self.width + x]
