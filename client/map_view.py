from kivy.properties import ObjectProperty
from kivy.lang import Builder

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
        StencilUnUse
{lightened_areas}
        StencilPop
'''



class MapView(RelativeWidget):
    groundTexture = ObjectProperty(None)

    def __init__(self, cellMap, character):
        self.groundTexture = utils.getTexture('wall2')
        self.map = cellMap
        self.char = character
        self.lightened_areas = []  # holes in the stencil
        self.always_visible = []

        for x in xrange(cellMap.width):
            for y in xrange(cellMap.height):
                section, value = cellMap.get_tile(x,y)
                if section == 'wa':
                    self.always_visible.append(Wall(pos=self.to_pixel((x, y))))
                elif section == 'it':
                    if value == cellMap.IT_TERMINAL:
                        self.always_visible.append(Terminal(pos=self.to_pixel((x, y))))
                elif section == 'vi':
                    if value == cellMap.IT_CAMERA:
                        # Somehow, Kivy doesn't update the view when the objects are in a list.
                        # Putting them as properties does the trick. Hence the __dict__ hack.
                        cam = Camera(pos=self.to_pixel((x,y)))
                        self.bind(pos=cam.update_pos)
                        self.lightened_areas.append(cam)
                        self.__dict__[cam.camname] = cam

        lightened_areas_kvstring = self.la_kv_string()
        print _MAP_VIEW_KV_TEMPLATE.format(
               lightened_areas=lightened_areas_kvstring)
        Builder.load_string(_MAP_VIEW_KV_TEMPLATE.format(
            lightened_areas=lightened_areas_kvstring))

        super(MapView, self).__init__(size=self.to_pixel(cellMap.size),
                                      pos=(0, 0))

        for obj in self.always_visible:
            self.add_widget(obj)
            self.bind(pos=obj.update_pos)

    def la_kv_string(self):
        output = []
        for cam in self.lightened_areas:
            output.append(cam.kv_string('self.' + cam.camname))
        output.append(self.char.get_vision().kv_string('self.char.get_vision()'))
        return ''.join(output)

    def to_pixel(self, coord):
        return (coord[0] * c.CELL_SIZE,
                coord[1] * c.CELL_SIZE)
