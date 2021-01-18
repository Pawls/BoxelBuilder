import math

import pyglet
from pyglet import window
from pyglet.gl import *
from pyglet.gl import glDisable, GL_CULL_FACE, GL_DEPTH_TEST, glViewport, glMatrixMode, GL_PROJECTION, glLoadIdentity, \
    glOrtho, GL_MODELVIEW, glEnable, glDepthFunc, GL_LESS, gluPerspective, glRotatef, glTranslatef
from pyglet.window import FPSDisplay

from camera import Camera
from grid import Grid
from sensor import Sensor
from world import World


class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sensor = Sensor()
        self.setup()
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
        # self.world.random_build()
        pyglet.clock.schedule(self.update)

    def label_update(self):
        """
        Refreshes screen text after resizing window
        """
        self.label = pyglet.text.Label('Move = W,A,S,D\tUp\\Down = R\\F',
                                       font_name='Calibri',
                                       font_size=12,
                                       x=2, y=self.height - 15, multiline=True, width=120)

    def adjust_stage_height(self, direction):
        self.grid.scroll(direction)
        self.sensor.move_y(direction)

    def on_mouse_scroll(self, x, y, mouse, direction):
        self.adjust_stage_height(direction)

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

    def on_key_press(self, button, modifiers):

        if button == window.key.ESCAPE:
            self.close()
        speed = 1
        if button == window.key.W:
            self.camera.strafe[0] = -speed
        elif button == window.key.S:
            self.camera.strafe[0] = speed
        elif button == window.key.A:
            self.camera.strafe[2] = -speed
        elif button == window.key.D:
            self.camera.strafe[2] = speed
        elif button == window.key.R:
            self.camera.strafe[1] = speed
        elif button == window.key.F:
            self.camera.strafe[1] = -speed
        elif button == window.key.RETURN:
            self.sensor.input_enter()
        elif button == window.key.NUM_ADD:
            self.world.tex_index += 1
            self.world.tex_index %= len(self.world.tex_lst)
            self.cursor_block.update_texture(self.world)
        elif button == window.key.NUM_SUBTRACT:
            self.world.tex_index -= 1
            self.world.tex_index %= len(self.world.tex_lst)
            self.cursor_block.update_texture(self.world)
        elif button == window.key.F11:
            self.world.save()
        elif button == window.key.F12:
            self.world.load()
        elif button == window.key.NUM_1:
            pass
        elif button == window.key.NUM_2:
            self.sensor.move_z(1)
        elif button == window.key.NUM_3:
            pass
        elif button == window.key.NUM_4:
            self.sensor.move_x(-1)
        elif button == window.key.NUM_5:
            self.sensor.commit_blocks(self.world)
        elif button == window.key.NUM_6:
            self.sensor.move_x(1)
        elif button == window.key.NUM_7:
            pass
        elif button == window.key.NUM_8:
            self.sensor.move_z(-1)
        elif button == window.key.NUM_9:
            self.world.random_build()
            #pass
        elif button == window.key.PAGEUP:
            self.adjust_stage_height(1)
        elif button == window.key.PAGEDOWN:
            self.adjust_stage_height(-1)

    def on_key_release(self, button, modifiers):
        if button == window.key.W:
            self.camera.strafe[0] = 0
        elif button == window.key.S:
            self.camera.strafe[0] = 0
        elif button == window.key.A:
            self.camera.strafe[2] = 0
        elif button == window.key.D:
            self.camera.strafe[2] = 0
        elif button == window.key.R:
            self.camera.strafe[1] = 0
        elif button == window.key.F:
            self.camera.strafe[1] = 0

    def update(self, dt):
        self.sensor.update(self.world)
        self.sync_frame += dt
        self.sync_frame %= 4  # modulus by max animation frames

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

    def on_draw(self):
        self.clear()
        self.set_3d()
        self.grid.draw()
        self.world.draw()
        if not tuple(self.cursor_block.position) in self.world.boxel_hash:
            self.cursor_block.batch.draw()
        self.sensor.draw()
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
        glClearColor(0.3, 0.8, 0.96, 1)  # Background color (r,g,b,a)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_CULL_FACE)
        self.setup_fog()


