import time
import tkinter as tk
from OpenGL import GL
from pyopengltk import OpenGLFrame
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk
import moderngl as mgl
import moderngl_window as mglw
import glm
import math


import colorsys


class AppOgl(OpenGLFrame):

    def initgl(self):
        # Initalize gl states when the frame is created
        # Prevent re-initialization on window resize
        if hasattr(self, "ctx"):
            return

        self.ctx = mgl.create_context()

        # Verify the detected context version and renderer
        print(
            f"Detected Context: {self.ctx.info['GL_RENDERER']} (OpenGL {self.ctx.version_code})"
        )

        # print(self.ctx.screen)
        self.ctx.viewport = (0, 0, self.width, self.height)
        # GL.glViewport(0, 0, self.width, self.height)
        # GL.glClearColor(0.0, 1.0, 0.0, 0.0)
        self.start = time.time()
        self.nframes = 0
        self.program = self.ctx.program(
            vertex_shader="""
                #version 330 core

                uniform mat4 projection;
                layout (location = 0) in vec3 in_vertex;

                void main() {
                    gl_Position = projection * vec4(in_vertex, 1.0);
                }
            """,
            fragment_shader="""
                #version 330 core

                layout (location = 0) out vec4 out_color;

                void main() {
                    out_color = vec4(1.0, 1.0, 1.0, 1.0);
                }
            """,
        )

        vertices = np.array([-0.5, -0.5, 0.0, 0.5, -0.5, 0.0, 0.0, 0.5, 0.0])

        self.vbo = self.ctx.buffer(vertices.astype("f4").tobytes())
        self.vao = self.ctx.vertex_array(self.program, [(self.vbo, "3f", "in_vertex")])

    def redraw(self):
        """Render a single frame"""
        # Update viewport to match current window size (handles resize)
        self.ctx.viewport = (0, 0, self.width, self.height)

        # Calculate aspect ratio and projection matrix
        aspect = self.width / self.height if self.height > 0 else 1.0
        # Orthographic projection: left, right, bottom, top, near, far
        # This keeps the vertical scale fixed (-1 to 1) and adjusts horizontal
        proj = glm.ortho(-aspect, aspect, -1.0, 1.0, -1.0, 1.0)
        self.program["projection"].write(proj)

        tm = time.time() - self.start
        refclr = colorsys.hsv_to_rgb(tm / 10, 1, 1)
        # GL.glClearColor(refclr[0], refclr[1], refclr[2], 0.0)
        # GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        self.nframes += 1
        self.ctx.clear(refclr[0], refclr[1], refclr[2], 0.0)
        self.ctx.enable(self.ctx.DEPTH_TEST)
        self.vao.render()
        # print("fps", self.nframes / tm, end="\r")


root = ctk.CTk()
root.geometry("1024x768")

conpan = ctk.CTkFrame(root, fg_color="grey")
conpan.pack(fill=tk.Y, expand=tk.NO, side="right")
conpan["width"] = "300"
conpan.pack_propagate(0)

abutton = ctk.CTkButton(
    conpan,
    text="Button",
)
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
# child2.after(100, child2.printContext)

data = {"x": [1, 2, 3, 4], "y": [1, 2, 3, 4]}
fig = plt.figure()
fig.add_subplot(111).plot(data["x"], data["y"])

child3 = FigureCanvasTkAgg(fig, master=stage).get_tk_widget()

child1.grid(row=0, column=0, sticky="nsew")
child3.grid(row=0, column=1, sticky="nsew")
child2.grid(row=1, column=0, columnspan=2, sticky="nsew")


def on_closing():
    # child2.animate = 0
    # root.after(100, root.destroy)
    # root.after_cancel()
    root.quit()


root.protocol("WM_DELETE_WINDOW", on_closing)


# app = AppOgl(root, width=320, height=200)
# app.pack(fill=tk.BOTH, expand=tk.YES)
# app.animate = 1
# app.after(100, app.printContext)
# app.mainloop()

colour = ["red", "green", "blue"]
cctr = 0


def CBHDLR():
    # print("aaa")
    global cctr
    child1.config(bg=colour[cctr % 3])
    cctr += 1
    root.after(160, CBHDLR)


root.after(160, CBHDLR)
root.mainloop()
# while True:
#     root.update()
