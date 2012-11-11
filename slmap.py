#!/usr/bin/python
# -*- coding: utf-8 -*-

class SLMap:
    # Header parsing stage
    MAP_TITLE, MAP_DIMENSIONS = range(0, 2)
    HEADER_PARSED = -1

    # Body directives
    SPAWN_DIRECTIVE, WALL_DIRECTIVE, ITEM_DIRECTIVE = range(0, 3)
    NO_DIRECTIVE = -1

    # Spawn points types
    MERCENARY_SPAWN, SPY_SPAWN = range(0, 2)

    def __init__(self, filename):
        self.load(filename)


    def load(self, filename):
        mapfile = open(filename, "r")

        if mapfile.readline() != "SLMap 1\n":
            return False

        headerStage = self.MAP_TITLE # No header line parsed yet.
        currentDirective = self.NO_DIRECTIVE # No directive found yet.

        for line in mapfile:
            line = line.strip()
            lineSplit = line.split()

            if line == "":
                # Empty line
                continue

            elif line[0] == "#":
                # Comment
                continue

            # Header parsing
            elif headerStage == self.MAP_TITLE:
                # Map title
                self.title = line
                headerStage = self.MAP_DIMENSIONS # Now, we know the title of the map

            elif headerStage == self.MAP_DIMENSIONS:
                # Map dimensions
                self.width, self.height = [int(_) for _ in lineSplit]
                self.spawnPoints = list()
                self.walls = list()
                self.wallType = [-1] * (self.width * self.height)
                self.itemType = [-1] * (self.width * self.height)
                headerStage = self.HEADER_PARSED # Now, we know the size of the map
                                                 # Header reading done

            # Body parsing
            elif lineSplit[0] == "sp:":
                # Spawn point directive
                currentDirective = self.SPAWN_DIRECTIVE

            elif lineSplit[0] == "wa:":
                # Wall directive beginning
                currentDirective = self.WALL_DIRECTIVE

            elif lineSplit[0] == "it:":
                # Item directive beginning
                currentDirective = self.ITEM_DIRECTIVE

            # Put other directives here!

            elif currentDirective == self.WALL_DIRECTIVE:
                # Spawn point directive
                x, y, t = [int(_) for _ in line.split(",")]
                self.spawnPoints[t] = (x, y)

            elif currentDirective == self.WALL_DIRECTIVE:
                # Wall directive
                x, y, t = [int(_) for _ in line.split(",")]
                self.walls.append((x, y, t))
                self.wallType[y * self.width + x] = t

            elif currentDirective == self.ITEM_DIRECTIVE:
                # Item directive
                x, y, t = [int(_) for _ in line.split(",")]
                self.itemType[y * self.width + x] = t

        mapfile.close()


    def getWallType(self, x, y):
        return self.wallType[y * self.width + x]

    def getItem(self, x, y):
        return self.itemType[y * self.width + x]
