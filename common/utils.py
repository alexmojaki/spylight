from shapely.geometry import Polygon

def create_square_from_top_left_coords(self, top, left, side_size):
	return Polygon(((left, top), (left + side_size, top), (left + side_size, top + side_size), (left, top + side_size)))