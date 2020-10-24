

class Boxel:
    inc = 0

    def __init__(self, xyz, tex, dim=(1, 1, 1)):
        self.batch = pyglet.graphics.Batch()
        self.position = list(xyz)
        self.dim = list(dim) # width, height, length
        self.tex_index = tex
        self.tex_name = tex_lst[self.tex_index][0]
        self.texture = load_texture(f"assets/textures/boxels/{self.tex_name}")
        self.alpha = 1
        # if 'water' in self.tex_name.split('_')[0]:
        #     self.alpha -= 0.25
        self.draw_block(xyz)

    def update_anim(self, dt):
        anim_frame = math.floor(sync_frame) % len(tex_lst[self.tex_index])
        self.batch = pyglet.graphics.Batch()
        self.texture = load_texture(f"assets/textures/boxels/{tex_lst[self.tex_index][anim_frame]}")
        self.draw_block(self.position)

    def update(self, dt):
        self.inc = (self.inc + math.pi * dt) % (2*math.pi)
        self.dim = [x + (dt * math.sin(self.inc)/6) for x in self.dim]
        self.batch = pyglet.graphics.Batch()
        self.draw_block(self.position)

    # I have yet to discover how the entire texture is mapped to the cube
    # using only texture coords (0,0)-(5/8,3/4). It should have been
    # incrementing by (1/5,1/3) until it reached (1,1) based on the fact
    # that the texture is 5 squares wide and 3 squares high.
    def draw_block(self, position):
        x, y, z = position
        dim = self.dim
        alpha = self.alpha
        self.batch.add(
            14,
            GL_TRIANGLE_STRIP,
            self.texture,
            ("v3f/static", (x + dim[0], y, z,  # 1
                            x, y, z,  # 2
                            x + dim[0], y, z + dim[2],  # 3
                            x, y, z + dim[2],  # 4
                            x, y + dim[1], z + dim[2],  # 5
                            x, y, z,  # 6
                            x, y + dim[1], z,  # 7
                            x + dim[0], y, z,  # 8
                            x + dim[0], y + dim[1], z,  # 9
                            x + dim[0], y, z + dim[2],  # 10
                            x + dim[0], y + dim[1], z + dim[2],  # 11
                            x, y + dim[1], z + dim[2],  # 12
                            x + dim[0], y + dim[1], z,  # 13
                            x, y + dim[1], z  # 14
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
                            255, 255, 255, alpha,  # 1255
                            255, 255, 255, alpha,  # 11
                            255, 255, 255, alpha,  # 12
                            255, 255, 255, alpha,  # 13
                            255, 255, 255, alpha  # 14
                            )
             )
        )


class CursorBlock(Boxel):
    inc = 0

    def __init__(self, xyz, tex, dim=(1, 1, 1)):
        self.batch = pyglet.graphics.Batch()
        self.position = list(xyz)
        self.dim = list(dim) # width, height, length
        self.tex_index = tex
        tex_name = tex_lst[self.tex_index][0]
        self.texture = load_texture(f"assets/textures/boxels/{tex_name}")
        self.alpha = 0.75
        # if 'water' in tex_name.split('_')[0]:
        #     self.alpha -= 0.25
        self.draw_block(xyz)

    def update_position(self, xyz):
        self.position = list(xyz)
        self.position[0] += (1 - self.dim[0]) / 2
        self.position[1] += (1 - self.dim[1]) / 2
        self.position[2] += (1 - self.dim[2]) / 2
        self.batch = pyglet.graphics.Batch()
        self.draw_block(self.position)

    def update_texture(self):
        self.texture = load_texture(f"assets/textures/boxels/{tex_lst[tex_index][0]}")
        self.batch = pyglet.graphics.Batch()
        self.draw_block(self.position)

    def update(self, dt):
        pass
        #self.inc = (self.inc + math.pi * dt) % (2*math.pi)
        #self.dim = [x + (dt * math.sin(self.inc)/6) for x in self.dim]