import math


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