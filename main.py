from tkinter import *

from pyglet.gl import *

from window import Window

if __name__ == "__main__":
    root = Tk()
    root.geometry('200x150')
    root.withdraw()
    Window(width=800, height=480, resizable=True, vsync=False)
    pyglet.app.run()
