import pickle
from itertools import groupby
from os import listdir
from os.path import isfile, join
from tkinter.filedialog import asksaveasfile, askopenfile

import pyglet
from pyglet.gl import glTexParameteri, GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST, GL_TEXTURE_MAG_FILTER

from boxel import Boxel, CursorBlock


class World:

    def __init__(self):
        self.tex_index = 0
        self.tex_lst = self.init_textures()
        self.init_textures()
        self.boxel = Boxel(self, (0, 0, 0), 0)  # Delete after UML generated
        self.boxel = CursorBlock(self, (0, 0, 0)) # Delete after UML generated
        self.boxel = []

    # Look in "assets/textures/boxels/*" for all textures
    def init_textures(self):
        path = "assets/textures/boxels/"
        tex_lst = [f for f in listdir(path) if isfile(join(path, f))]
        tex_lst.sort()
        tex_lst = [list(i) for j, i in groupby(tex_lst, lambda a: a.split('_')[0])]
        for x in tex_lst:
            for y in range(len(x)):
                texture = pyglet.resource.texture(path + x[y])
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
                x[y] = pyglet.graphics.TextureGroup(texture)
        return tex_lst

    #  Saves the current boxel world to a file
    def save(self):
        files = [('World File', '*.wld')]
        file = asksaveasfile(filetypes=files, defaultextension=files)
        if file:
            f = open(file.name, "wb")
            data = []
            for box in self.boxel:
                data.append([box.tex_index, box.position])
            pickle.dump(data, f)
            f.close()

    def load(self):
        file_types = [('World File', '*.wld')]
        file = askopenfile(filetypes=file_types, defaultextension=file_types)
        if file:
            f = open(file.name, "rb")
            data = pickle.load(f)
            self.boxel = []
            for i, j in data:
                self.add_block(j, i)
            f.close()

    def create_cursor(self):
        return CursorBlock(self, (0, 0, 0))

    def add_block(self, xyz, tex=False):
        for x in list(self.boxel):
            if x.position == list(xyz):
                return
        self.boxel.append(Boxel(self, xyz, tex))

    def del_block(self, xyz):
        for x in list(self.boxel):
            if x.position == list(xyz):
                self.boxel.remove(x)
                return

    def stress_test(self):
        for i in range(3, 13):
            for j in range(3, 13):
                for k in range(16):
                    self.add_block((i, k, j))

    def update(self, dt, sync):
        for x in self.boxel:
            x.update(dt, sync)

    def draw(self):
        for x in self.boxel:
            x.batch.draw()
