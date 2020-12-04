import serial
from pyglet.gl import GL_QUADS, glFrontFace, GL_CCW, GL_CW

from boxel import CursorBlock
from pyglet import graphics
from pyglet.gl import GL_TRIANGLE_STRIP


class Sensor:

    def __init__(self):
        # Setup Sensor if connected
        #self.boxel = CursorBlock(self, (0, 0, 0))  # Delete after UML generated
        self.boxel = []
        self.total_serial_inputs = 0
        self.ser = None
        self.position = (0, 0, 0)
        self.dim = (3, 3, 3)  # width, height, depth
        try:
            self.ser = serial.Serial('COM3', 9600, timeout=0.050)
            self.ser.flushInput()
        except IOError:
            print("Sensor not connected...")

    def input_enter(self):
        self.ser.write("\n".encode())

    def move_x(self, distance):
        x, y, z = self.position
        x += distance
        self.position = (x, y, z)
        for ele in self.boxel:
            x, y, z = ele.position
            x += distance
            ele.update_position((x, y, z))

    def move_y(self, distance):
        x, y, z = self.position
        y += distance
        self.position = (x, y, z)
        for ele in self.boxel:
            x, y, z = ele.position
            y += distance
            ele.update_position((x, y, z))

    def move_z(self, distance):
        x, y, z = self.position
        z += distance
        self.position = (x, y, z)
        for ele in self.boxel:
            x, y, z = ele.position
            z += distance
            ele.update_position((x, y, z))

    def commit_blocks(self, world):
        x, y, z = self.position
        width, length, height = self.dim
        for w in range(width):
            for l in range(length):
                for h in range(height):
                    world.del_block((x + w, y + h, z + l))
        for ele in self.boxel:
            world.add_block(ele.position, ele.tex_index)

    def add_cursorblock(self, world, xyz):
        for x in list(self.boxel):
            if x.position == list(xyz):
                return
        self.boxel.append(CursorBlock(world, xyz))

    def del_cursorblock(self, xyz):
        for x in list(self.boxel):
            if x.position == list(xyz):
                self.boxel.remove(x)
                return

    def draw_sensor(self):
        x, y, z = self.position
        w, h, d = self.dim
        overlap = 0.05
        x += overlap
        z += overlap
        y += overlap
        w -= overlap * 2
        h -= overlap * 2
        d -= overlap * 2
        dx, dy, dz = x + w, y + h, z + d
        alpha = 0.25
        graphics.draw(
            20,
            GL_QUADS,
            ("v3f/static", (x, y, z, x, y, dz, x, dy, dz, x, dy, z,  # side
                            dx, y, dz, dx, y, z, dx, dy, z, dx, dy, dz,  # side
                            dx, y, z, x, y, z, x, dy, z, dx, dy, z,  # side
                            x, y, dz, dx, y, dz, dx, dy, dz, x, dy, dz,  # side
                            x, y, z, dx, y, z, dx, y, dz, x, y, dz)  # bottom
             ),
            ("c4f/static", (255, 255, 255, alpha,  # 1
                            255, 255, 255, alpha,  # 2
                            255, 255, 255, alpha,  # 3
                            255, 255, 255, alpha,  # 4
                            255, 255, 255, alpha,  # 5
                            255, 255, 255, alpha,  # 6
                            255, 255, 255, alpha,  # 7
                            255, 255, 255, alpha,  # 8
                            255, 255, 0, alpha,  # 9
                            255, 255, 0, alpha,  # 10
                            255, 255, 0, alpha,  # 11
                            255, 255, 0, alpha,  # 12
                            255, 255, 0, alpha,  # 13
                            255, 255, 0, alpha,  # 14
                            255, 255, 0, alpha,  # 15
                            255, 255, 0, alpha,  # 16
                            255, 0, 0, alpha,  # 17
                            255, 0, 0, alpha,  # 18
                            255, 0, 0, alpha,  # 19
                            255, 0, 0, alpha  # 20
                            )
             )
        )

    def draw(self):
        self.draw_sensor()
        for x in self.boxel:
            x.batch.draw()

    def update(self, world):
        if self.ser:
            while self.ser.in_waiting:
                x, y, z = self.position
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
                                    self.del_cursorblock((x + row, i - 1 + y, z + column))
                                else:
                                    self.add_cursorblock(world, (x + row, i - 1 + y, z + column))

