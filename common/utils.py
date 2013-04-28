from shapely.geometry import Polygon
import game_constants as const

def create_square_from_top_left_coords(top, left, side_size):
	return Polygon(((left, top), (left + side_size, top), (left + side_size, top + side_size), (left, top + side_size)))

# multiply a tuple by a real and returns a tuple
# @param{tuple} the_tuple tuple to be multiplied
# @param{integer, float} multiplier
# @return{tuple} the_tuple multiplied by the multiplier
def mt(the_tuple, multiplier):
	return tuple([i*multiplier for i in the_tuple])

def norm_to_cell(coord):
        return int(coord // const.CELL_SIZE)
