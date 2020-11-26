import math
from pyglet import graphics
from pyglet.gl import glLineWidth, GL_LINES, GL_LINE_STRIP


class Grid:

    def __init__(self, column, row):
        self.columns = 16
        self.rows = 16
        self.ratio = self.rows / self.columns
        self.level = 0
        self.factor = (column, row)
        self.size = 1

    # Get grid sector from mouse click
    def select(self, x, y, camera, window):
        cam_dir, cam_pitch = camera.rotation
        cam_fov = 45
        cell_size = 1
        level = self.level

        display_w, display_h = window.get_size()
        aspect = display_w / display_h
        mouse_x = x
        mouse_y = display_h - y
        x, y, z = camera.position
        ss = round(math.cos(math.radians(-cam_dir)), 2)
        cc = round(math.sin(math.radians(-cam_dir)), 2)
        vector_x = round(cc * math.cos(math.radians(cam_pitch)), 2)
        vector_y = round(math.sin(math.radians(cam_pitch)), 2)
        vector_z = round((ss * -math.cos(math.radians(cam_pitch))), 2)

        # get the magnitude
        mag = math.sqrt(vector_x * vector_x + vector_y * vector_y + vector_z * vector_z)

        # Error correction
        if mag == 0:
            mag = .0001

        # Normalize the vector
        vector_x /= mag
        vector_y /= mag
        vector_z /= mag

        uX = 0
        uY = 1
        uZ = 0
        mag = uX * vector_x + uY * vector_y + uZ * vector_z
        uX -= mag * vector_x
        uY -= mag * vector_y
        uZ -= mag * vector_z
        mag = math.sqrt(uX * uX + uY * uY + uZ * uZ)

        # Error correction
        if mag == 0:
            mag = .0001

        uX /= mag
        uY /= mag
        uZ /= mag

        tFOV = math.tan(math.radians(cam_fov) / 2)
        uX *= tFOV
        uY *= tFOV
        uZ *= tFOV

        vX = uY * vector_z - vector_y * uZ
        vY = uZ * vector_x - vector_z * uX
        vZ = uX * vector_y - vector_x * uY

        # Correct for aspect ratio
        vX *= aspect
        vY *= aspect
        vZ *= aspect

        xscreen = 2 * mouse_x / display_w - 1
        yscreen = 1 - 2 * mouse_y / display_h

        mX = vector_x + uX * yscreen + vX * xscreen
        mY = vector_y + uY * yscreen + vY * xscreen
        mZ = vector_z + uZ * yscreen + vZ * xscreen
        if mY == 0:
            mY = .0001

        mousex = round((x - cell_size / 2 + (y - level) * mX / mY))
        mousey = round((z - cell_size / 2 - (y - level) * mZ / mY))
        return (mousex, level, mousey)

    def scroll(self, distance):
        self.level += int(distance)

    def draw(self):
        x, y = self.factor
        glLineWidth(5)
        # Draw y-axis (green)
        graphics.draw(2, GL_LINES,
                      ('v3i', (0, 0, 0, 0, y * self.rows, 0)),
                      ('c3B', (0, 255, 0, 0, 255, 0))
                      )
        # Draw x-axis (red)
        graphics.draw(2, GL_LINES,
                      ('v3i', (0, 0, 0, self.columns * x, 0, 0)),
                      ('c3B', (255, 0, 0, 255, 0, 0))
                      )
        # Draw z-axis (blue)
        graphics.draw(2, GL_LINES,
                      ('v3i', (0, 0, 0, 0, 0, y * self.rows)),
                      ('c3B', (0, 0, 255, 0, 0, 255))
                      )
        glLineWidth(1)
        # Draw outer grid
        graphics.draw(5, GL_LINE_STRIP,
                      ('v3i', (0, self.size * self.level, 0, self.columns * x, self.size * self.level, 0, self.columns * x,
                               self.size * self.level, y * self.rows, 0, self.size * self.level, y * self.rows, 0,
                               self.size * self.level, 0)),
                      ('c3B', (255, 0, 0, 255, 0, 0, 0, 0, 0, 0, 0, 255, 0, 0, 255))
                      )
        # Draw the inner grid
        for i in range(1, self.columns):
            graphics.draw(2, GL_LINES,
                          ('v3i', (i * x, self.size * self.level, 0, i * x, self.size * self.level, y * self.rows)),
                          ('c3B', (0, 0, 255, 0, 0, 0))
                          )
        for i in range(1, self.rows):
            graphics.draw(2, GL_LINES,
                          ('v3i', (0, self.size * self.level, i * y, x * self.columns, self.size * self.level, i * y)),
                          ('c3B', (255, 0, 0, 0, 0, 0))
                          )