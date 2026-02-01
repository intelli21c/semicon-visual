import time
import tkinter as tk
from OpenGL import GL
from pyopengltk import OpenGLFrame
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import colorsys


class AppOgl(OpenGLFrame):

    def initgl(self):
        """Initalize gl states when the frame is created"""
        GL.glViewport(0, 0, self.width, self.height)
        GL.glClearColor(0.0, 1.0, 0.0, 0.0)
        self.start = time.time()
        self.nframes = 0

    def redraw(self):
        """Render a single frame"""
        tm = time.time() - self.start
        refclr = colorsys.hsv_to_rgb(tm / 10, 1, 1)
        GL.glClearColor(refclr[0], refclr[1], refclr[2], 0.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        self.nframes += 1
        #print("fps", self.nframes / tm, end="\r")


root = tk.Tk()
root.geometry("1024x768")

conpan = tk.Frame(root, bg="grey")
conpan.pack(fill=tk.Y, expand=tk.NO, side="right")
conpan["width"] = "300"
conpan.pack_propagate(0)

abutton = tk.Button(conpan, text="Button", )
abutton.pack()

stage = tk.Frame(root)
stage.pack(fill=tk.BOTH, expand=tk.YES, side="left")
for i in range(2):
    stage.grid_rowconfigure(i, weight=1)
    stage.grid_columnconfigure(i, weight=1)

child1 = tk.Frame(stage, width=200, bg="red")
# child1.pack(fill=tk.BOTH, expand=tk.NO)

child2 = AppOgl(stage, width=200, height=200)
# child2.pack(fill=tk.BOTH, expand=tk.YES, anchor="nw")
child2.animate = 1
#child2.after(100, child2.printContext)

data = {"x": [1, 2, 3, 4], "y": [1, 2, 3, 4]}
fig = plt.figure()
fig.add_subplot(111).plot(data["x"], data["y"])

child3 = FigureCanvasTkAgg(fig, master=stage).get_tk_widget()

child1.grid(row=0, column=0, sticky="nsew")
child3.grid(row=0, column=1, sticky="nsew")
child2.grid(row=1, column=0, columnspan=2, sticky="nsew")

def on_closing():
    #child2.animate = 0
    #root.after(100, root.destroy)
    #root.after_cancel()
    root.quit()

root.protocol("WM_DELETE_WINDOW", on_closing)


# app = AppOgl(root, width=320, height=200)
# app.pack(fill=tk.BOTH, expand=tk.YES)
# app.animate = 1
# app.after(100, app.printContext)
root.mainloop()
# app.mainloop()
