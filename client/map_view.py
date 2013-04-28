from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.logger import Logger

import common.game_constants as c
from client import utils
from client.environment import RelativeWidget, Camera, Wall, Terminal


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
{hidden}
        StencilUnUse
{lightened_areas}
        StencilPop
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

        # We have to sort the various items to display depending on the layer
        # where we want to put them

        # Sorting the items from the map
        for x in xrange(cellMap.width):
            for y in xrange(cellMap.height):
                section, value = cellMap.get_tile(x, y)
                if section == 'wa':
                    self.always_visible.append(Wall(pos=self._to_pixel((x, y))))
                elif section == 'it':
                    if value == cellMap.IT_TERMINAL:
                        self.always_visible.append(
                            Terminal(pos=self._to_pixel((x, y))))
                elif section == 'vi':
                    if value == cellMap.IT_CAMERA:
                        # Somehow, Kivy doesn't update the view when the
                        # objects are in a list. Putting them as properties
                        # does the trick. Hence the __dict__ hack.
                        cam = Camera(pos=self._to_pixel((x, y)),
                                     dir=cellMap.get_camera_orientation(x, y))
                        self.bind(pos=cam.update_pos)
                        self.lightened_areas.append(cam)
                        self.__dict__[cam.kvname] = cam

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

        super(MapView, self).__init__(size=self._to_pixel(cellMap.size),
                                      pos=(0, 0))

        for obj in self.always_visible:
            self.add_widget(obj)
            self.bind(pos=obj.update_pos)

        for obj in self.lightened_areas:  # To add the object's sprite
            self.add_widget(obj)

        self.add_widget(character)

    def _process_kv_template(self):
        la = []
        for l_area in self.lightened_areas:
            la.append(l_area.kv_string('self.' + l_area.kvname))
        la.append(self.char.get_vision().kv_string('self.char.get_vision()'))

        h = []
        for hidden_obj in self.hidden:
            print 'pos', hidden_obj.pos
            h.append(hidden_obj.kv_string('self.' + hidden_obj.kvname))

        return _MAP_VIEW_KV_TEMPLATE.format(lightened_areas=''.join(la),
                                            hidden=''.join(h))

    def _to_pixel(self, coord):
        return (coord[0] * c.CELL_SIZE,
                coord[1] * c.CELL_SIZE)

    def update(self, data):
        self._update_visible_objects(data['vo'])

    def _update_visible_objects(self, vo):
        self.visible_objects
        pass
