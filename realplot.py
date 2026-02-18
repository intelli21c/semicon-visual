import time
import tkinter as tk

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk

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

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 10))
canvas = FigureCanvasTkAgg(fig, master=root)
tkFig = canvas.get_tk_widget()
tkFig.pack(side="left", expand=True, fill=tk.BOTH)


def on_closing():
    root.quit()


root.protocol("WM_DELETE_WINDOW", on_closing)


import matplotlib.pyplot as plt


class Point:
    def __init__(self, x):
        self.x = x
        self.eDen = 0.0
        self.hDen = 0.0
        self.doping = 0.0
        self.E = 0.0
        self.V = 0.0


def UpdatePhysics(points):
    # 1. Calculate Electric Field (Integral of Net Charge)
    curr_E = 0
    for p in points:
        # Net Charge = Holes - Electrons + Doping Ions
        rho = p.hDen - p.eDen + p.doping
        curr_E += rho
        p.E = curr_E

    # Center the Field so it is 0 at the neutral ends
    offset = (points[0].E + points[-1].E) / 2
    for p in points:
        p.E -= offset

    # 2. Calculate Potential (Negative Integral of E)
    curr_V = 0
    for p in points:
        p.V = curr_V
        curr_V -= p.E


def TransportSolver(points, dt, diff_const, recomb_rate):
    # A. Move Charges (Drift + Diffusion)
    for i in range(len(points) - 1):
        lp, rp = points[i], points[i + 1]
        avg_E = (lp.E + rp.E) / 2

        # Electrons: Drift opposite to E, Diffusion from High to Low
        j_e = (avg_E * rp.eDen if avg_E > 0 else avg_E * lp.eDen) * dt
        j_e += diff_const * (rp.eDen - lp.eDen) * dt

        # Holes: Drift with E, Diffusion from High to Low
        j_h = (-avg_E * lp.hDen if avg_E > 0 else -avg_E * rp.hDen) * dt
        j_h += diff_const * (rp.hDen - lp.hDen) * dt

        # Conservation update
        rp.eDen -= j_e
        lp.eDen += j_e
        rp.hDen -= j_h
        lp.hDen += j_h

    # B. Recombination: This stops the "waves" by letting overlap settle
    for p in points:
        # Simple law of mass action: rate is proportional to n * p
        annihilation = p.eDen * p.hDen * recomb_rate * dt
        p.eDen -= annihilation
        p.hDen -= annihilation
        # Ensure density never goes negative
        p.eDen = max(0, p.eDen)
        p.hDen = max(0, p.hDen)


# --- 1. SETUP ---
points = [Point(i) for i in range(100)]
for p in points:
    if p.x < 50:
        p.doping = -2.0  # P-side
        p.hDen = 2.0
    else:
        p.doping = 2.0  # N-side
        p.eDen = 2.0

# for _ in range(30000):
#     UpdatePhysics(points)
#     TransportSolver(points, dt=0.005, diff_const=0.2, recomb_rate=0.5)


def CBHDLR():
    # --- 2. RUN ---
    # More iterations with a smaller dt = smooth convergence
    UpdatePhysics(points)
    TransportSolver(points, dt=0.005, diff_const=0.2, recomb_rate=0.5)

    # --- 3. PLOT ---
    x = [p.x for p in points]
    rho = [(p.hDen - p.eDen + p.doping) for p in points]
    field = [p.E for p in points]
    potential = [p.V for p in points]

    ax1.clear()
    ax2.clear()
    ax3.clear()

    ax1.fill_between(x, rho, color="gray", alpha=0.3)
    ax1.plot(x, [p.eDen for p in points], label="Electrons (n)", color="blue")
    ax1.plot(x, [p.hDen for p in points], label="Holes (p)", color="red")
    ax1.set_title("Carrier Densities & Space Charge")
    ax1.legend()

    ax2.plot(x, field, color="green")
    ax2.set_title("Electric Field (Downward Peak at Junction)")

    ax3.plot(x, potential, color="orange")
    ax3.set_title("Electrostatic Potential")

    canvas.draw()
    root.after(16, CBHDLR)
    #root.after_idle(CBHDLR)


root.after(160, CBHDLR)
root.mainloop()
