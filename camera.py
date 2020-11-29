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
        x, y, z = self.position
        motion_vector = self.get_motion_vector()
        speed = dt * 5
        new_x = x + motion_vector[0] * speed
        new_y = y + motion_vector[1] * speed
        new_z = z + motion_vector[2] * speed
        self.position = [new_x, new_y, new_z]

    def get_motion_vector(self):
        x, y, z = self.strafe
        if x or z:
            strafe = math.atan2(x, z)
            yaw = math.radians(self.rotation[0])
            x = math.cos(yaw + strafe)
            z = math.sin(yaw + strafe)
        return x, y, z