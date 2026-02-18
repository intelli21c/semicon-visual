import math
import numpy
import matplotlib.pyplot as plt

# constants
timeStep = 0.1

mobility = 1
temp = 273


class Point:
    # to have - charge density, electric field strength
    def __init__(self, x):
        self.x = x
        self.eDen = 0
        self.hDen = 0
        self.qDopant = 0
        self.E = 0  # electric field
        # below are non-atomic? values
        self.V = 0
        self.EF = 0  # fermi level (from doping density)
        self.QF = 0  # quasi-fermi level

    def __repr__(self):
        return f"Point(x={self.x:.2f})"

    @staticmethod
    def UpdateVArr(points):
        l = len(points)
        points[0].V = 0
        for i in range(1, l):
            points[i].V = points[i - 1].V - points[i].E
        # points[l - 1].V = 0

    @staticmethod
    def PopulatePointArray(length, interval, start=0):
        iters = int(length / interval)
        return [Point(start + i * interval) for i in range(iters)]


def CrudeMN(points):
    midpoint = (len(points) / 2) - 1
    for point in points:
        point.eDen = 99
        point.qDopant = 99  # more of a "nuclear field"
        if point.x > midpoint:
            point.eDen = 10
            point.qDopant = 10


def Poission(points: Point):  # more an gaussian E field solver, but...
    # imposing Boundary conditions
    midpoint = int(len(points) / 2) - 1
    points[len(points) - 1].E = 0
    for i in range(midpoint, len(points) - 1):
        points[i].E = points[i - 1].E + (
            -points[i].eDen + points[i].hDen + points[i].qDopant
        )  # *dx/(e0er)
    # roll-up voltage from E
    Point.UpdateVArr(points)


def DriftCurrent(points):
    midpoint = int(len(points) / 2) - 1
    jN = [0] * len(points)
    jP = [0] * len(points)
    for i in range(midpoint + 1, len(points) - 1):
        jN[i] = points[i].eDen * -points[i].E
    return jN, jP


def DiffusionCurrent(points):
    midpoint = int(len(points) / 2) - 1
    jN = [0] * len(points)
    jP = [0] * len(points)
    for i in range(midpoint + 1, len(points) - 1):
        g = points[i + 1].eDen - points[i].eDen  # carr. den. grad. from midpoint i.5
        jN[i] = -g  # *mob/T #(==Dn, einstein rel.)
    return jN, jP


def BarrierCurrent(points):
    jN = [0] * len(points)
    jP = [0] * len(points)
    midpoint = int(len(points) / 2) - 1
    SBH = (
        1 + points[midpoint].V - points[midpoint + 1].V
    )  # intrinsic V (Ef-Efi(N)) + bent V diff.
    biasV = -0.5
    jN[midpoint] = 1 * math.exp(-SBH) * (math.exp(biasV) - 1)
    return jN, jP


# points = Point.PopulatePointArray(100, 0.1)
points = Point.PopulatePointArray(100, 1)
CrudeMN(points)
print(f"Initial Density {[p.eDen for p in points]}")
midpoint = int(len(points) / 2) - 1
for i in range(200):
    Poission(points)
    jdiffn, jdiffp = DiffusionCurrent(points)
    jdrftn, jdrftp = DriftCurrent(points)
    jTE, _ = BarrierCurrent(points)
    for j in range(midpoint, len(points) - 1):
        jtotN_right = jdrftn[j] + jdiffn[j] + jTE[j]
        jtotN_left = jdrftn[j - 1] + jdiffn[j - 1] + jTE[j - 1]

        fluxN = (jtotN_right - jtotN_left) * timeStep

        points[j].eDen -= fluxN

    print(f"EQL? max J : {max([a + b for a, b in zip(jdrftn, jdiffn)])}")
    print(f"Iter {i} space charge {[(-p.eDen+p.hDen+p.qDopant) for p in points]}")
    print(f"Iter {i} density {[(p.eDen) for p in points]}")
    if i > 100 and i % 10 == 0:
        x = [p.x for p in points]
        fig, (ax1, ax4, ax2, ax3) = plt.subplots(4, 1, figsize=(8, 10))
        ax1.axvspan(0, midpoint, color="lightgrey", label="Metal")
        ax2.axvspan(0, midpoint, color="lightgrey", label="Metal")
        ax3.axvspan(0, midpoint, color="lightgrey", label="Metal")
        ax4.axvspan(0, midpoint, color="lightgrey", label="Metal")
        ax1.plot(x, [p.eDen for p in points], label="Electrons (n)", color="blue")
        ax1.plot(
            x,
            [(-p.eDen + p.qDopant) for p in points],
            label="Space Charge",
            color="grey",
        )
        ax1.set_title("Carrier Densities")
        ax1.legend()
        ax4.plot(
            x,
            jdrftn,
            label="drift current",
            color="red",
        )
        ax4.plot(
            x,
            jdiffn,
            label="diffusion current",
            color="blue",
        )
        ax4.bar(
            midpoint,
            jTE[midpoint],
            width=1.0,
            color="black",
            label="Thermionic Emission",
        )

        ax4.plot(
            x,
            [a + b for a, b in zip(jdrftn, jdiffn)],
            label="Flux",
            color="green",
        )
        ax4.set_title("Electron Flux(Right is positive)")
        ax4.legend()

        # J should be 0 at eql but should be present for realtime plotting.

        ax2.plot(x, [p.E for p in points], color="green")
        ax2.set_title("Electric Field")

        ax3.plot(x, [-p.V for p in points], color="orange")
        ax3.set_title(
            "Electron Energy (also Vacuum Level bending)"
        )  # "Electrostatic Potential")

        plt.tight_layout()
        plt.show()

# x = [p.x for p in points]
# fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 10))
# ax1.plot(x, [p.eDen for p in points], label="Electrons (n)", color="blue")
# ax1.plot(x, [p.hDen for p in points], label="Holes (p)", color="red")
# ax1.plot(
#     x,
#     [(-p.eDen + p.hDen + p.qDopant) for p in points],
#     label="Space Charge",
#     color="grey",
# )
# ax1.set_title("Carrier Densities")
# ax1.legend()

# # J should be 0 at eql but should be present for realtime plotting.

# ax2.plot(x, [p.E for p in points], color="green")
# ax2.set_title("Electric Field")

# ax3.plot(x, [-p.V for p in points], color="orange")
# ax3.set_title("Electron Energy (also Vacuum Level bending)")  # "Electrostatic Potential")

# plt.tight_layout()
# plt.show()
