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

    @staticmethod
    def SetMaterialBatch(points, materialList):
        # assumed input - [[(0 ,50), n], [(50,100), p]]... like this
        for region in materialList:
            for point in points:
                if region[0] <= point.x <= region[1]:
                    point.material = region[2]
                    # point=region[2](point)  //(setdoping())
                    # maybe it will be the material condition handler - like doping den. setter but good for now.
                    break
        return points


def CrudePN(points):
    midpoint = (len(points) / 2) - 1
    for point in points:
        if point.x < midpoint:
            point.hDen = 10
            point.qDopant = -10
        elif point.x > midpoint:
            point.eDen = 10
            point.qDopant = 10


def Poission(points: Point):  # more an gaussian E field solver, but...
    points[0].E = 0
    points[len(points) - 1].E = 0
    # first/end not needed.
    for i in range(1, len(points) - 1):
        points[i].E = points[i - 1].E + (
            -points[i].eDen + points[i].hDen + points[i].qDopant
        )  # *dx/(e0er)
    # roll-up voltage from E
    Point.UpdateVArr(points)


def DriftCurrent(points):
    jN = [0] * len(points)
    jP = [0] * len(points)
    for i in range(len(points) - 1):
        jN[i] = points[i].eDen * -points[i].E
        jP[i] = points[i].hDen * points[i].E
    return jN, jP


def DiffusionCurrent(points):
    jN = [0] * len(points)
    jP = [0] * len(points)
    for i in range(len(points) - 1):
        g = points[i + 1].eDen - points[i].eDen  # carr. den. grad. from midpoint i.5
        jN[i] = -g  # *mob/T #(==Dn, einstein rel.)
        g = points[i + 1].hDen - points[i].hDen
        jP[i] = -g
    return jN, jP


# points = Point.PopulatePointArray(100, 0.1)
points = Point.PopulatePointArray(100, 1)
CrudePN(points)
print(f"Initial Density {[p.eDen for p in points]}")
for i in range(140):
    Poission(points)
    jdiffn, jdiffp = DiffusionCurrent(points)
    jdrftn, jdrftp = DriftCurrent(points)
    # for j in range(len(points) - 2):
    #     points[j + 1].eDen += jdrftn[j] + jdiffn[j]
    #     points[j].eDen -= jdrftn[j] + jdiffn[j]
    #     points[j + 1].hDen += jdrftp[j] + jdiffp[j]
    #     points[j].hDen -= jdrftp[j] + jdiffp[j]

    # for j in range(1, len(points) - 1):
    #     gradJn = jdrftn[j] + jdiffn[j] - (jdrftn[j - 1] + jdiffn[j - 1])
    #     gradJp = jdrftp[j] + jdiffp[j] - (jdrftp[j - 1] + jdiffp[j - 1])
    #     fluxN = gradJn * timeStep
    #     fluxP = gradJp * timeStep
    #     points[j].eDen -= fluxN
    #     points[j].hDen -= fluxP

    for j in range(len(points) - 1):
        Jn = jdrftn[j] + jdiffn[j]
        Jp = jdrftp[j] + jdiffp[j]

        dN = Jn * timeStep
        dP = Jp * timeStep

        points[j].eDen -= dN
        points[j + 1].eDen += dN

        points[j].hDen -= dP
        points[j + 1].hDen += dP

    print(f"EQL? max J : {max([a + b for a, b in zip(jdrftn, jdiffn)])}")
    print(f"Iter {i} space charge {[(-p.eDen+p.hDen+p.qDopant) for p in points]}")
    print(f"Iter {i} density {[(p.eDen) for p in points]}")
    if i % 10 == 0 or i > 40:
        # if i % 10 == 0:
        x = [p.x for p in points]
        fig, (ax1, ax4, ax2, ax3) = plt.subplots(4, 1, figsize=(8, 10))
        ax1.plot(x, [p.eDen for p in points], label="Electrons (n)", color="blue")
        ax1.plot(x, [p.hDen for p in points], label="Holes (p)", color="red")
        ax1.plot(
            x,
            [(-p.eDen + p.hDen + p.qDopant) for p in points],
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
