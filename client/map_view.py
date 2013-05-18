from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.logger import Logger

import common.game_constants as c
from common.map_parser import SpyLightMap
from client import utils
from client.environment import RelativeWidget, Camera, VertWall, HorizWall, BlockWall, Terminal


_MAP_VIEW_KV_TEMPLATE = '''
<MapView>:
    size_hint: None, None
    canvas:
        StencilPush
{lightened_areas}
        StencilUse
            func_op: 'lequal'
        Rectangle:
            pos: self.pos
            size: self.size
            texture:self.groundTexture
            tex_coords: self.tex_coords
{hidden}
        StencilUnUse
{lightened_areas}
        StencilPop
{always_visible}
'''


class MapView(RelativeWidget):
    groundTexture = ObjectProperty(None)

    def __init__(self, cellMap, character, players):
        self.groundTexture = utils.getTexture('wall2')
        self.map = cellMap
        self.char = character
        self.lightened_areas = []  # holes in the stencil
        self.always_visible = []  # displayed on top of the stencil
        self.hidden = []  # hidden by the stencil
        self.visible_objects = {}  # vo, grouped by type id and then coord.

        self.tmp_walls = {}  # Used to build the walls, will be deleted and
                             # the walls will only be available through __dict__

        # We have to sort the various items to display depending on the layer
        # where we want to put them

        # Sorting the items from the map
        for x in xrange(cellMap.width):
            for y in xrange(cellMap.height):
                section, value = cellMap.get_tile(x, y)
                obj = None
                if section == 'wa':
                    self._build_wall(x, y, value)
                elif section == 'it':
                    if value == cellMap.IT_TERMINAL:
                        obj = Terminal(pos=self._to_pixel((x, y)))
                        self.always_visible.append(obj)
                elif section == 'vi':
                    if value == cellMap.IT_CAMERA:
                        obj = Camera(pos=self._to_pixel((x, y)),
                                     dir=cellMap.get_camera_orientation(x, y))
                        self.lightened_areas.append(obj)
                if obj:
                    self.bind(pos=obj.update_pos)
                    # Somehow, Kivy doesn't update the view when the
                    # objects are in a list. Putting them as properties
                    # does the trick. Hence the __dict__ hack.
                    self.__dict__[obj.kvname] = obj

        # Sorting the players
        for i in players:
            player = players[i]
            if player.playerid != character.playerid:
                self.bind(pos=player.update_pos)
                self.__dict__[player.kvname] = player
                self.hidden.append(player)

        # We can process the view template to get the final kv.
        final_kv = self._process_kv_template()
        Logger.info("SL|MapView: Final kv file: %s", final_kv)
        Builder.load_string(final_kv)

        # Fix the texture scaling.
        size = self._to_pixel(cellMap.size)
        nb_repeat_x = size[0] / c.CELL_SIZE
        nb_repeat_y = size[1] / c.CELL_SIZE
        self.tex_coords = (
            0, 0,
            nb_repeat_x, 0,
            nb_repeat_x, -nb_repeat_y,
            0, -nb_repeat_y
        )

        super(MapView, self).__init__(size=size, pos=(0, 0))

        for obj in self.lightened_areas:  # To add the object's sprite
            self.add_widget(obj)

        self.add_widget(character)

    def _process_kv_template(self):
        la = []
        for l_area in self.lightened_areas:
            la.append(l_area.kv_string('self.' + l_area.kvname))
        self.char_vision = self.char.get_vision()
        la.append(self.char.get_vision().kv_string('self.char_vision'))

        h = []
        for hidden_obj in self.hidden:
            h.append(hidden_obj.kv_string('self.' + hidden_obj.kvname))

        av = []
        for visible in self.always_visible:
            av.append(visible.kv_string('self.' + visible.kvname))

        return _MAP_VIEW_KV_TEMPLATE.format(lightened_areas=''.join(la),
                                            always_visible=''.join(av),
                                            hidden=''.join(h))

    def _to_pixel(self, coord):
        return (coord[0] * c.CELL_SIZE,
                coord[1] * c.CELL_SIZE)

    def update(self, data):
        #self._update_visible_objects(data['vo'])
        # TODO?
        pass

    def _update_visible_objects(self, vo):
        pass

    def _build_wall(self, x, y, wall_type):
        previous_wall = None
        # Look for an existing wall to which the current tile is a section
        try:
            if wall_type == SpyLightMap.WA_HORIZ:  # -
                previous_wall = self.tmp_walls[x-1][y]
            elif wall_type == SpyLightMap.WA_VERT:  # |
                previous_wall = self.tmp_walls[x][y-1]
            #elif wall_type == SpyLightMap.WA_BLOCK:  # +
            #   previous_wall = None
        except KeyError:
            previous_wall = None

        # Add or update the wall
        if previous_wall and previous_wall.type == wall_type:
            previous_wall.add_section(*self._to_pixel((x, y)))
            self._set_tmp_wall(x, y, previous_wall)
        else:
            self._create_wall(x, y, wall_type)

    def _set_tmp_wall(self, x, y, obj):
        if not x in self.tmp_walls:
            self.tmp_walls[x] = {}

        assert y not in self.tmp_walls[x]
        if y in self.tmp_walls[x]:  # Something is wrong
            raise KeyError('The tile ({}, {}) is already occupied: {}'
                           .format(x, y, self.tmp_walls[x][y]))
        else:
            self.tmp_walls[x][y] = obj

    def _create_wall(self, x, y, wall_type):
        wall = None
        if wall_type == SpyLightMap.WA_VERT:  # |
            wall = VertWall(pos=self._to_pixel((x, y)), type=wall_type)
        elif wall_type == SpyLightMap.WA_HORIZ:  # -
            wall = HorizWall(pos=self._to_pixel((x, y)), type=wall_type)
        elif wall_type == SpyLightMap.WA_BLOCK:  # +
            wall = BlockWall(pos=self._to_pixel((x, y)), type=wall_type)
        else:
            raise AttributeError('Unknown wall type: {}'.format(wall_type))

        self._set_tmp_wall(x, y, wall)
        self.always_visible.append(wall)
        self.bind(pos=wall.update_pos)
        self.__dict__[wall.kvname] = wall
