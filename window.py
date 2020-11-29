import math

import pyglet
import serial
from pyglet import window
from pyglet.gl import *
from pyglet.gl import glDisable, GL_CULL_FACE, GL_DEPTH_TEST, glViewport, glMatrixMode, GL_PROJECTION, glLoadIdentity, \
    glOrtho, GL_MODELVIEW, glEnable, glDepthFunc, GL_LESS, gluPerspective, glRotatef, glTranslatef
from pyglet.window import FPSDisplay

from camera import Camera
from grid import Grid
from world import World


class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup()
        self.ser = self.init_sensor()
        self.total_serial_inputs = 0
        self.world = World()
        self.sync_frame = 0
        self.mouse_pos = (0, 0)
        self.frame_rate = 1 / 60
        self.fps_display = FPSDisplay(self)
        self.grid = Grid()
        self.camera = Camera()
        self.cursor_block = self.world.create_cursor()
        self.label = pyglet.text.Label('Move = W,A,S,D\tUp\\Down = R\\F',
                                       font_name='Calibri',
                                       font_size=12,
                                       x=2, y=self.height - 15, multiline=True, width=120)
        # stress_test()
        pyglet.clock.schedule(self.update)

    def label_update(self):
        """
        Refreshes screen text after resizing window
        """
        self.label = pyglet.text.Label('Move = W,A,S,D\tUp\\Down = R\\F',
                                       font_name='Calibri',
                                       font_size=12,
                                       x=2, y=self.height - 15, multiline=True, width=120)

    def on_mouse_scroll(self, x, y, mouse, direction):
        self.grid.scroll(direction)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == window.mouse.LEFT:
            xyz = self.grid.select(x, y, self.camera, self)
            self.world.add_block(xyz)
        elif button == window.mouse.RIGHT:
            xyz = self.grid.select(x, y, self.camera, self)
            self.world.del_block(xyz)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.mouse_pos = (x, y)
        if button == window.mouse.MIDDLE:
            self.camera.mouse_motion(dx, dy)
        elif button == window.mouse.LEFT:
            xyz = self.grid.select(x, y, self.camera, self)
            self.world.add_block(xyz)
        elif button == window.mouse.RIGHT:
            xyz = self.grid.select(x, y, self.camera, self)
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

        mouse_over = self.grid.select(*self.mouse_pos, self.camera, self)
        self.cursor_block.update_position(mouse_over)
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
        glOrtho(0, max(1, width), 0, max(1, height), -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_3d(self):
        width, height = self.get_size()
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
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
        self.grid.draw()
        self.world.draw()
        self.cursor_block.batch.draw()
        self.set_2d()
        self.fps_display.draw()
        self.label.draw()

    def setup_fog(self):
        glEnable(GL_FOG)
        glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))
        glHint(GL_FOG_HINT, GL_DONT_CARE)
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogf(GL_FOG_START, 20.0)
        glFogf(GL_FOG_END, 60.0)

    def setup(self):
        # Background color (r,g,b,a)
        glClearColor(0.3, 0.8, 0.96, 1)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CW)
        self.setup_fog()
