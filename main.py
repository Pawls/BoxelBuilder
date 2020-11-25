import math
import pickle
import pyglet
import serial
from itertools import groupby
from os import listdir
from os.path import isfile, join
from tkinter import *
from tkinter.filedialog import asksaveasfile, askopenfile
from pyglet import window, graphics
from pyglet.gl import *
from pyglet.window import FPSDisplay


class World:

    def __init__(self):
        self.boxel = []
        self.tex_index = 0
        self.tex_lst = self.init_textures()
        self.init_textures()

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
    def save(self, world):
        files = [('World File', '*.wld')]
        file = asksaveasfile(filetypes=files, defaultextension=files)
        f = open(file.name, "wb")
        data = []
        for box in world:
            data.append([box.tex_index, box.position])
        pickle.dump(data, f)
        f.close()

    def load(self):
        file_types = [('World File', '*.wld')]
        file = askopenfile(filetypes=file_types, defaultextension=file_types)
        f = open(file.name, "rb")
        data = pickle.load(f)
        world = []
        for i, j in data:
            self.add_block(j, i)
        f.close()
        return world

    def create_cursor(self):
        return CursorBlock(self, (0, 0, 0))

    def add_block(self, xyz):
        for x in list(self.boxel):
            if x.position == list(xyz):
                return
        self.boxel.append(Boxel(self, xyz))

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


class Boxel:
    inc = 0

    def __init__(self, parent, xyz, dim=(1, 1, 1)):
        self.batch = pyglet.graphics.Batch()
        self.position = list(xyz)
        self.dim = list(dim)  # width, height, length
        self.tex_index = parent.tex_index
        self.tex_sequence = parent.tex_lst[self.tex_index]
        self.texture = self.tex_sequence[0]
        self.alpha = 1
        self.draw_block(xyz)

    def update_anim(self, dt):
        pass
        #anim_frame = math.floor(sync_frame) % len(tex_lst[self.tex_index])
        # self.batch = pyglet.graphics.Batch()
        # self.texture = tex_lst[self.tex_index][anim_frame]
        # self.draw_block(self.position)

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

    def __init__(self, parent, xyz, dim=(1, 1, 1)):
        self.batch = pyglet.graphics.Batch()
        self.position = list(xyz)
        self.dim = list(dim)  # width, height, length
        self.tex_index = parent.tex_index
        self.tex_sequence = parent.tex_lst[self.tex_index]
        self.texture = self.tex_sequence[0]
        self.alpha = 0.75
        self.draw_block(xyz)

    def update_position(self, xyz):
        self.position = list(xyz)
        self.position[0] += (1 - self.dim[0]) / 2
        self.position[1] += (1 - self.dim[1]) / 2
        self.position[2] += (1 - self.dim[2]) / 2
        self.batch = pyglet.graphics.Batch()
        self.draw_block(self.position)

    def update_texture(self, parent):
        self.texture = parent.tex_lst[parent.tex_index][0]
        self.batch = pyglet.graphics.Batch()
        self.draw_block(self.position)

    def update(self, dt):
        pass
        #self.inc = (self.inc + math.pi * dt) % (2*math.pi)
        #self.dim = [x + (dt * math.sin(self.inc)/6) for x in self.dim]


# def block_hover(xyz, dt, sync_frame):
#     for i in list(boxel):
#         if i.position == list(xyz):
#             i.update(dt, sync_frame)
#             return


class Camera:
    def __init__(self, position=(1.5, 4, 9), rotation=(0, -18)):
        self.position = position
        self.rotation = rotation
        self.strafe = [0, 0, 0]  # forward, up, left

    def mouse_motion(self, dx, dy):
        x, y = self.rotation
        sensitivity = 0.15
        x -= dx * sensitivity
        y -= dy * sensitivity
        y = max(-90, min(90, y))
        self.rotation = x % 360, y

    def update(self, dt):
        motion_vector = self.get_motion_vector()
        speed = dt * 5
        self.position = [x + y * speed for x, y in zip(self.position, motion_vector)]

    def get_motion_vector(self):
        x, y, z = self.strafe
        if x or z:
            strafe = math.degrees(math.atan2(x, z))
            yaw = self.rotation[0]
            x_angle = math.radians(yaw + strafe)
            x = math.cos(x_angle)
            z = math.sin(x_angle)
        return x, y, z


class Grid:
    COLUMNS = 16
    ROWS = 16
    SIZE = 1
    RATIO = ROWS / COLUMNS
    level = 0

    factor = (1, 1)

    def __init__(self, column, row, offset_x=0, offset_y=0):
        column *= self.COLUMNS
        row *= self.ROWS
        if not (0 < column <= self.COLUMNS):
            raise IndexError('{} is not in the grid (0, {})'.format(
                column, self.COLUMNS
            ))
        if not (0 < row <= self.ROWS):
            raise IndexError('{} is not in the grid (0, {})'.format(
                row, self.ROWS
            ))
        x, y = self.factor

    @classmethod
    def scrollGrid(cls, distance):
        cls.level += int(distance)

    @classmethod
    def draw_grid(cls):
        x, y = cls.factor
        glLineWidth(5)
        # Draw y-axis (green)
        graphics.draw(2, GL_LINES,
                      ('v3i', (0, 0, 0, 0, y * cls.ROWS, 0)),
                      ('c3B', (0, 255, 0, 0, 255, 0))
                      )
        # Draw x-axis (red)
        graphics.draw(2, GL_LINES,
                      ('v3i', (0, 0, 0, cls.COLUMNS * x, 0, 0)),
                      ('c3B', (255, 0, 0, 255, 0, 0))
                      )
        # Draw z-axis (blue)
        graphics.draw(2, GL_LINES,
                      ('v3i', (0, 0, 0, 0, 0, y * cls.ROWS)),
                      ('c3B', (0, 0, 255, 0, 0, 255))
                      )
        glLineWidth(1)
        # Draw outer grid
        graphics.draw(5, GL_LINE_STRIP,
                      ('v3i', (0, cls.SIZE * cls.level, 0, cls.COLUMNS * x, cls.SIZE * cls.level, 0, cls.COLUMNS * x,
                               cls.SIZE * cls.level, y * cls.ROWS, 0, cls.SIZE * cls.level, y * cls.ROWS, 0,
                               cls.SIZE * cls.level, 0)),
                      ('c3B', (255, 0, 0, 255, 0, 0, 0, 0, 0, 0, 0, 255, 0, 0, 255))
                      )
        # Draw the inner grid
        for i in range(1, cls.COLUMNS):
            graphics.draw(2, GL_LINES,
                          ('v3i', (i * x, cls.SIZE * cls.level, 0, i * x, cls.SIZE * cls.level, y * cls.ROWS)),
                          ('c3B', (0, 0, 255, 0, 0, 0))
                          )
        for i in range(1, cls.ROWS):
            graphics.draw(2, GL_LINES,
                          ('v3i', (0, cls.SIZE * cls.level, i * y, x * cls.COLUMNS, cls.SIZE * cls.level, i * y)),
                          ('c3B', (255, 0, 0, 0, 0, 0))
                          )


class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ser = self.init_sensor()
        self.total_serial_inputs = 0
        self.world = World()
        self.sync_frame = 0
        self.mouse_pos = (0, 0)
        self.frame_rate = 1 / 60
        self.fps_display = FPSDisplay(self)
        self.grid = Grid(1, 1, 0, 0)
        self.camera = Camera()
        self.cursor_block = self.world.create_cursor()
        self.label = pyglet.text.Label('Move = W,A,S,D\tUp\\Down = R\\F',
                                       font_name='Calibri',
                                       font_size=12,
                                       x=2, y=self.height - 15, multiline=True, width=120)

        # self.label = pyglet.text.Label('HELLOOOAOJFOJDSFOAJSDFOJAOIEJ', font_name='Arial', font_size=18,
        #     x=10, y=self.height - 10, anchor_x='left', anchor_y='top',
        #     color=(255,255,255, 255))

        # stress_test()
        pyglet.clock.schedule(self.update)

    def label_update(self):
        self.label = pyglet.text.Label('Move = W,A,S,D\tUp\\Down = R\\F',
                                       font_name='Calibri',
                                       font_size=12,
                                       x=2, y=self.height - 15, multiline=True, width=120)

    def on_mouse_scroll(self, x, y, mouse, direction):
        self.grid.scrollGrid(direction)

    # Get grid sector from mouse click
    def grid_select(self, x, y):
        camDir, camPitch = self.camera.rotation
        camFOV = 45
        useGrid = 1
        level = self.grid.level

        display_w, display_h = self.get_size()
        aspect = display_w / display_h
        mouse_x = x
        mouse_y = display_h - y
        x, y, z = self.camera.position
        ss = round(math.cos(math.radians(-camDir)), 2)
        cc = round(math.sin(math.radians(-camDir)), 2)
        vector_x = round(cc * math.cos(math.radians(camPitch)), 2)
        vector_y = round(math.sin(math.radians(camPitch)), 2)
        vector_z = round((ss * -math.cos(math.radians(camPitch))), 2)
        dX = (x + vector_x) - x
        dY = (y + vector_y) - y
        dZ = (z + vector_z) - z
        mm = math.sqrt(dX * dX + dY * dY + dZ * dZ)
        if mm == 0:
            mm = .0001
        dX /= mm
        dY /= mm
        dZ /= mm

        uX = 0
        uY = 1
        uZ = 0
        mm = uX * dX + uY * dY + uZ * dZ
        uX -= mm * dX
        uY -= mm * dY
        uZ -= mm * dZ
        mm = math.sqrt(uX * uX + uY * uY + uZ * uZ)
        if mm == 0:
            mm = .0001
        uX /= mm
        uY /= mm
        uZ /= mm

        tFOV = math.tan(math.radians(camFOV) / 2)
        uX *= tFOV
        uY *= tFOV
        uZ *= tFOV

        vX = uY * dZ - dY * uZ
        vY = uZ * dX - dZ * uX
        vZ = uX * dY - dX * uY

        vX *= aspect
        vY *= aspect
        vZ *= aspect

        xscreen = 2 * mouse_x / display_w - 1
        yscreen = 1 - 2 * mouse_y / display_h

        mX = dX + uX * yscreen + vX * xscreen
        mY = dY + uY * yscreen + vY * xscreen
        mZ = dZ + uZ * yscreen + vZ * xscreen
        if mY == 0:
            mY = .0001

        mousex = round((x - useGrid / 2 + (y - level) * mX / mY))
        mousey = round((z - useGrid / 2 - (y - level) * mZ / mY))
        return (mousex, level, mousey)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == window.mouse.LEFT:
            xyz = self.grid_select(x, y)
            self.world.add_block(xyz)
        elif button == window.mouse.RIGHT:
            xyz = self.grid_select(x, y)
            self.world.del_block(xyz)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.mouse_pos = (x, y)
        if button == window.mouse.MIDDLE:
            self.camera.mouse_motion(dx, dy)
        elif button == window.mouse.LEFT:
            xyz = self.grid_select(x, y)
            self.world.add_block(xyz)
        elif button == window.mouse.RIGHT:
            xyz = self.grid_select(x, y)
            self.world.del_block(xyz)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_pos = (x, y)

    def on_key_press(self, symbol, modifiers):

        if symbol == window.key.ESCAPE:
            self.close()
        speed = 1
        if symbol == window.key.W:
            self.camera.strafe[0] = -speed
        elif symbol == window.key.S:
            self.camera.strafe[0] = speed
        elif symbol == window.key.A:
            self.camera.strafe[2] = -speed
        elif symbol == window.key.D:
            self.camera.strafe[2] = speed
        elif symbol == window.key.R:
            self.camera.strafe[1] = speed
        elif symbol == window.key.F:
            self.camera.strafe[1] = -speed
        elif symbol == window.key.RETURN:
            self.ser.write("\n".encode())
        elif symbol == window.key.NUM_ADD:
            self.world.tex_index += 1
            self.world.tex_index %= len(self.world.tex_lst)
            self.cursor_block.update_texture(self.world)
        elif symbol == window.key.NUM_SUBTRACT:
            self.world.tex_index -= 1
            self.world.tex_index %= len(self.world.tex_lst)
            self.cursor_block.update_texture(self.world)
        elif symbol == window.key.F11:
            self.world.save()
        elif symbol == window.key.F12:
            self.world.load()

    def on_key_release(self, symbol, modifiers):
        if symbol == window.key.W:
            self.camera.strafe[0] = 0
        elif symbol == window.key.S:
            self.camera.strafe[0] = 0
        elif symbol == window.key.A:
            self.camera.strafe[2] = 0
        elif symbol == window.key.D:
            self.camera.strafe[2] = 0
        elif symbol == window.key.R:
            self.camera.strafe[1] = 0
        elif symbol == window.key.F:
            self.camera.strafe[1] = 0

    def update(self, dt):
        self.update_sensor()
        self.sync_frame += dt
        # modulus by max animation frames
        self.sync_frame %= 4

        mouse_over = self.grid_select(*self.mouse_pos)
        self.cursor_block.update_position(mouse_over)
        #block_hover(mouse_over, dt, self.sync_frame)
        self.cursor_block.update(dt)
        self.camera.update(dt)
        self.world.update(dt, self.sync_frame)

    def set_2d(self):
        width, height = self.get_size()
        glDisable(GL_CULL_FACE)
        glDisable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        #gluOrtho2D(0, width, 0, height)
        glOrtho(0, max(1, width), 0, max(1, height), -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_3d(self):
        width, height = self.get_size()
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        #glDepthFunc(GL_LEQUAL)
        glDepthFunc(GL_LESS)
        viewport = self.get_viewport_size()
        #glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        yaw, pitch = self.camera.rotation
        glRotatef(yaw, 0, 1, 0)
        glRotatef(-pitch, math.cos(math.radians(yaw)), 0, math.sin(math.radians(yaw)))
        x, y, z = self.camera.position
        glTranslatef(-x, -y, -z)

    def on_resize(self, width, height):
        width, height = self.get_size()
        self.label_update()
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        return pyglet.event.EVENT_HANDLED

    def init_sensor(self):
        # Setup Sensor if connected
        ser = False
        try:
            ser = serial.Serial('COM3', 9600, timeout=0.050)
            ser.flushInput()
        except:
            print("Sensor not connected...")
        finally:
            return ser

    def update_sensor(self):

        try:
            while self.ser.in_waiting:
                sensor_input = self.ser.readline()
                read_sensor = sensor_input.decode()
                print(read_sensor)
                self.total_serial_inputs += 1
                if self.total_serial_inputs > 2:
                    sensor_objects = read_sensor.split()
                    for row in range(3):
                        for column in range(3):
                            block_stack = int(sensor_objects[row * 3 + column])
                            for i in range(1, 4):
                                if i > block_stack:
                                    self.world.del_block((row, i - 1, column))
                                else:
                                    self.world.add_block((row, i - 1, column))
        except:
            pass

    def on_draw(self):
        self.clear()
        self.set_3d()
        self.grid.draw_grid()
        self.world.draw()
        self.cursor_block.batch.draw()
        self.set_2d()
        self.fps_display.draw()
        self.label.draw()


def setup_fog():
    glEnable(GL_FOG)
    glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))
    glHint(GL_FOG_HINT, GL_DONT_CARE)
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogf(GL_FOG_START, 20.0)
    glFogf(GL_FOG_END, 60.0)


def setup():
    # Background color (r,g,b,a)
    glClearColor(0.3, 0.8, 0.96, 1)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glFrontFace(GL_CW)
    setup_fog()



if __name__ == "__main__":
    root = Tk()
    root.geometry('200x150')
    root.withdraw()
    Window(width=800, height=480, resizable=True, vsync=False)
    # Window(fullscreen=True)
    setup()
    pyglet.app.run()
