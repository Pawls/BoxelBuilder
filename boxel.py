import math

import pyglet
from pyglet.gl import GL_TRIANGLE_STRIP


class Boxel:
    inc = 0

    def __init__(self, parent, xyz, tex=None, dim=(1, 1, 1)):
        self.batch = pyglet.graphics.Batch()
        self.position = list(xyz)
        self.dim = list(dim)  # width, height, length
        if tex is None:
            self.tex_index = parent.tex_index
        else:
            self.tex_index = tex
        self.tex_sequence = parent.tex_lst[self.tex_index]
        self.texture = self.tex_sequence[0]
        self.alpha = 1
        self.draw_block(xyz)

    def update(self, dt, sync_frame):
        if len(self.tex_sequence) > 1:
            anim_frame = math.floor(sync_frame) % len(self.tex_sequence)
            self.batch = pyglet.graphics.Batch()
            self.texture = self.tex_sequence[anim_frame]
            self.draw_block(self.position)
        #self.inc = (self.inc + math.pi * dt) % (2*math.pi)
        #self.dim = [x + (dt * math.sin(self.inc)/6) for x in self.dim]
        #self.batch = pyglet.graphics.Batch()
        #self.draw_block(self.position)

    # I have yet to discover how the entire texture is mapped to the cube
    # using only texture coords (0,0)-(5/8,3/4). It should have been
    # incrementing by (1/5,1/3) until it reached (1,1) based on the fact
    # that the texture is 5 squares wide and 3 squares high.
    def draw_block(self, position, y_shift=0):
        x, y, z = position
        y += y_shift
        dim = self.dim
        w, h, d = self.dim
        alpha = self.alpha
        self.batch.add(
            14,
            GL_TRIANGLE_STRIP,
            self.texture,
            ("v3f/static", (x + w, y, z + d,  # 0
                            x, y, z + d,  # 1
                            x + w, y, z,  # 2
                            x, y, z,  # 3
                            x, y + h, z,  # 4
                            x, y, z + d,  # 1
                            x, y + h, z + d,  # 5
                            x + w, y, z + d,  # 0
                            x + w, y + h, z + d,  # 6
                            x + w, y, z,  # 2
                            x + w, y + h, z,  # 7
                            x, y + h, z,  # 4
                            x + w, y + h, z + d,  # 6
                            x, y + h, z + d  # 5
                            )
             ),
            ("t2f/static", (0, 0,  # 1
                            1 / 8, 0,  # 2
                            0, 1 / 4,  # 3
                            1 / 8, 1 / 4,  # 4
                            1 / 8, 2 / 4,  # 5
                            2 / 8, 1 / 4,  # 6
                            2 / 8, 2 / 4,  # 7
                            3 / 8, 1 / 4,  # 8
                            3 / 8, 2 / 4,  # 9
                            4 / 8, 1 / 4,  # 10
                            4 / 8, 2 / 4,  # 11
                            5 / 8, 2 / 4,  # 12
                            4 / 8, 3 / 4,  # 13
                            5 / 8, 3 / 4  # 14
                            )
             ),
            ("c4f/static", (255, 255, 255, alpha,  # 1
                            255, 255, 255, alpha,  # 2
                            255, 255, 255, alpha,  # 3
                            255, 255, 255, alpha,  # 4
                            255, 255, 255, alpha,  # 5
                            255, 255, 255, alpha,  # 6
                            255, 255, 255, alpha,  # 7
                            255, 255, 255, alpha,  # 8
                            255, 255, 255, alpha,  # 9
                            255, 255, 255, alpha,  # 12
                            255, 255, 255, alpha,  # 11
                            255, 255, 255, alpha,  # 12
                            255, 255, 255, alpha,  # 13
                            255, 255, 255, alpha  # 14
                            )
             )
        )


class CursorBlock(Boxel):

    def __init__(self, parent, xyz, dim=(1, 1, 1)):
        self.inc = 0
        self.batch = pyglet.graphics.Batch()
        self.position = list(xyz)
        self.dim = list(dim)  # width, height, length
        self.tex_index = parent.tex_index
        self.tex_sequence = parent.tex_lst[self.tex_index]
        self.texture = self.tex_sequence[0]
        self.alpha = 0.75
        self.draw_block(xyz)

    def update_position(self, xyz, y_shift=0):
        self.position = list(xyz)
        self.position[0] += (1 - self.dim[0]) / 2
        self.position[1] += (1 - self.dim[1]) / 2
        self.position[2] += (1 - self.dim[2]) / 2
        self.batch = pyglet.graphics.Batch()
        self.draw_block(self.position, y_shift)

    def update_texture(self, parent):
        self.texture = parent.tex_lst[parent.tex_index][0]
        self.batch = pyglet.graphics.Batch()
        self.draw_block(self.position)

    def update(self, dt):
        x, y, z = self.position
        amplitude = 0.05
        period = 2
        self.inc = (self.inc + math.pi * dt) % (2*math.pi)
        y_shift = amplitude * math.sin(period * self.inc) + amplitude
        self.update_position((x, y, z), y_shift)
