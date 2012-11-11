from kivy.vector import Vector
from math import cos

from slmap import SLMap

CELL_SIZE = 32
SIGHT_RANGE = 100

class Edge(Object):

	def __init__(self, p1, p2, distToChar):

        self.next = None
        # self.prev = None

        self.p1 = p1
        self.p2 = p2

        self.distToChar = distToChar

        self.intersect = None

    def compare(self, edge2):
    	return self.distToChar - edge2.distToChar

def createEdges():
	lst = list()

	for tabw in slmap.walls:
		x = tabw[0] * CELL_SIZE
		y = tabw[1] * CELL_SIZE
		typ = tabw[2] * CELL_SIZE

		p1 = Vector(persoX, persoY)
		p2 = Vector(x + CELL_SIZE/2, y + CELL_SIZE/2)

		distToChar = p1.distance(p2)
		if distToChar > SIGHT_RANGE:
			continue

		view = p2 - p1

		edges = list()

		for i in xrange(0,4):
			if i == 0 and typ not in [2,3,4,7,8,9,11,15]:
				p1 = Vector(x, y) # DOWN
				p2 = Vector(x+CELL_SIZE, y)
			elif i == 1 and typ not in [1,3,5,7,8,10,11,14]:
				p1 = Vector(x+CELL_SIZE, y) # RIGHT
				p2 = Vector(x+CELL_SIZE, y+CELL_SIZE)
			elif i == 2 and typ not in [2,5,6,7,9,10,11,13]:
				p1 = Vector(x+CELL_SIZE, y+CELL_SIZE) # UP
				p2 = Vector(x, y+CELL_SIZE)
			elif i == 3 and typ not in [1,4,6,8,9,10,11,12]:
				p1 = Vector(x, y+CELL_SIZE) # LEFT
				p2 = Vector(x, y)

			dire = p2 - p1

			norm = Vector(-dire[1], dire[0])

			if norm.dot(view) > 0:
				edge = Edge(p1, p2, distToChar)
				lst.append(edge)

	return lst

def setNeighbors(lstEdges):
	
	for edge1 in lstEdges:
		for edge2 in lstEdges:
			if edge1 != edge2:
				if edge1.p1.distance(edge2.p2) < 2:
					edge1.next = edge2
					# edge2.prev = edge1
				else
					for edge3 in lstEdges:
						x0 = persoX
						y0 = persoY
						xA = edge1.p1.x
						yA = edge1.p1.y
						xB = edge3.p1.x
						yB = edge3.p1.y
						xC = edge3.p2.x
						yC = edge3.p2.y

						if (xA-x0) * (yB-yC) != (xC - xB) * (y0-yA)
							edge1.next = edge3
						
				if edge1.p2.distance(edge2.p1) < 2:
					# edge1.prev = edge2
					edge2.next = edge1
				else
					for edge3 in lstEdges:
						x0 = persoX
						y0 = persoY
						xA = edge2.p2.x
						yA = edge2.p2.y
						xB = edge3.p1.x
						yB = edge3.p1.y
						xC = edge3.p2.x
						yC = edge3.p2.y

						if (xA-x0) * (yB-yC) != (xC - xB) * (y0-yA)
							edge3.next = edge2
 
def defineMesh(lstEdges):
	meshLst = list()

	orig = lstEdges[0]

	lst.append(orig.p1)
	next = orig.next

	while next != orig:

		x0 = persoX
		y0 = persoY
		xA = edge2.p2.x
		yA = edge2.p2.y
		xB = edge3.p1.x
		yB = edge3.p1.y
		xC = edge3.p2.x
		yC = edge3.p2.y

		

		lst.append

def pseudoMain():

	lst = createEdges()
	lst.sort(key=Edge.compare)

	setNeighbors(lst)

	mesh = defineMesh(lst)