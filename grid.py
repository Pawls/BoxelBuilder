import math

from pyglet import graphics
from pyglet.gl import glLineWidth, GL_LINES, GL_LINE_STRIP


class Grid:

    def __init__(self):
        self.columns = 16
        self.rows = 16
        self.ratio = self.rows / self.columns
        self.level = 0
        self.factor = (1, 1)
        self.size = 1

    # Get grid sector from mouse click
    def select(self, mouse_x, mouse_y, camera, window):
        cam_yaw, cam_pitch = (math.radians(x) for x in camera.rotation)
        cam_pitch = max(min(cam_pitch, 1.565), -1.565)  # Prevent pitch from being perfect vertical
        cam_fov = 45
        cell_size = 1
        level = self.level
        display_w, display_h = window.get_size()
        aspect = display_w / display_h
        mouse_y = display_h - mouse_y  # Flip the y-coordinate (OpenGL y-coord is inverted)
        x, y, z = camera.position

        # Get the sine and cosine components of the camera's pitch and yaw
        cos_yaw = math.cos(-cam_yaw)
        sin_yaw = math.sin(-cam_yaw)
        cos_pitch = math.cos(cam_pitch)
        sin_pitch = math.sin(cam_pitch)

        # Get the unit vector, d, representing the camera's direction
        dx = round(sin_yaw * cos_pitch, 2)
        dy = round(sin_pitch, 2)
        dz = round(cos_yaw * (-cos_pitch), 2)
        norm = math.sqrt(dx * dx + dy * dy + dz * dz)
        norm = max(norm, 0.00001)  # Prevent division by zero
        dx /= norm
        dy /= norm
        dz /= norm

        # Define the "up" vector
        ux, uy, uz = (0, 1, 0)
        # Get the dot product of U and D
        dot_prod = ux * dx + uy * dy + uz * dz
        # Orthogonal projection of U ("Up" vector) with D (the camera vector)
        ux -= dot_prod * dx
        uy -= dot_prod * dy
        uz -= dot_prod * dz
        # Normalize the new vector
        norm = math.sqrt(ux * ux + uy * uy + uz * uz)
        norm = max(norm, 0.00001)
        ux /= norm
        uy /= norm
        uz /= norm

        # Scale by the field of view
        fov = math.tan(math.radians(cam_fov) / 2)
        ux *= fov
        uy *= fov
        uz *= fov

        # V is the cross product of U and D (V is perpendicular to U and D)
        # It represents the x-axis of the screen.
        vx = uy * dz - dy * uz
        vy = uz * dx - dz * ux
        vz = ux * dy - dx * uy

        # Scale by the aspect ratio
        vx *= aspect
        vy *= aspect
        vz *= aspect

        xscreen = 2 * mouse_x / display_w - 1
        yscreen = 1 - 2 * mouse_y / display_h

        #  Create vector M which is the translation of D (the camera vector)
        #  by the location of the mouse click. U represents the y-axis on the screen
        #  while V represents the x-axis.
        mx = dx + ux * yscreen + vx * xscreen
        my = dy + uy * yscreen + vy * xscreen
        mz = dz + uz * yscreen + vz * xscreen
        if my == 0:
            my = 0.0001

        #  Finally, determine the cell on the plane that intersects vector M
        mouse_x = round((x - cell_size / 2 + (y - level) * mx / my))
        mouse_y = round((z - cell_size / 2 - (y - level) * mz / my))
        return mouse_x, level, mouse_y

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
        glLineWidth(2)
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
