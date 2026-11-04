"""
Bezier curve - Modelling of Curves and Surfaces, Programming Assignment 1
Pure Python 3 + tkinter (standard library only).

Run:  python main.py

Controls
  left click on empty canvas   add a control vertex v_i
  left drag on a vertex        move it
  right click on a vertex      delete it
  slider "Minimal sample length"  = epsilon (min 10)
  checkbox "Visualize computations" + slider t:
                               de Casteljau rows, point, tangent, normal
  "Reset"                      remove everything and start again
"""
import math
import tkinter as tk

W, H = 900, 650        # canvas size
PICK_RADIUS = 10       # how close (px) a click must be to grab a vertex
MAX_DEPTH = 20         # safety limit of the recursion


# ---------------------------------------------------------------------------
# Geometry (no GUI code here)
# ---------------------------------------------------------------------------
def lerp(a, b, t):
    """Point (1 - t) * a + t * b."""
    return ((1 - t) * a[0] + t * b[0], (1 - t) * a[1] + t * b[1])


def de_casteljau_rows(points, t):
    """
    De Casteljau algorithm. Returns all rows:
      rows[0] = the control points b_i^0,
      rows[k][i] = (1 - t) * rows[k-1][i] + t * rows[k-1][i+1],
      rows[n] = [b_0^n(t)]  -> the point on the curve.
    """
    rows = [list(points)]
    while len(rows[-1]) > 1:
        prev = rows[-1]
        rows.append([lerp(prev[i], prev[i + 1], t) for i in range(len(prev) - 1)])
    return rows


def split_half(points):
    """
    Split the curve at t = 1/2 into two Bezier curves of the same degree.
    Left  control points = first  point of every row  <b_0^k>,       k = 0..n
    Right control points = last   point of every row  <b_{n-k}^k>,   k = n..0
    """
    rows = de_casteljau_rows(points, 0.5)
    left = [row[0] for row in rows]
    right = [row[-1] for row in reversed(rows)]
    return left, right


def too_long(points, eps):
    """Condition (2): some polygon edge has length >= eps."""
    return any(math.dist(points[i + 1], points[i]) >= eps
               for i in range(len(points) - 1))


def adaptive_refine(points, eps, depth=0):
    """
    Adaptive refinement of the control polygon: while a polygon has an edge
    >= eps, split the curve at t = 1/2 and refine both halves.
    Returns a list of control polygons (one per final curve segment).
    """
    if len(points) < 2:
        return []
    if depth >= MAX_DEPTH or not too_long(points, eps):
        return [points]
    left, right = split_half(points)
    return adaptive_refine(left, eps, depth + 1) + adaptive_refine(right, eps, depth + 1)


# ---------------------------------------------------------------------------
# Application (look follows the sample application)
# ---------------------------------------------------------------------------
C_POLY, C_CURVE, C_ROW = "#9acd32", "#40d0d0", "#bbbbbb"   # polygon, curve, de Casteljau rows
C_VERTEX, C_POINT, C_TANGENT, C_NORMAL = "#d9534f", "black", "#008000", "#ff0000"


class App:
    def __init__(self, win):
        win.title("Bezier curve")
        self.pts = []          # control vertices v_0 .. v_n  (list of [x, y])
        self.drag = None       # index of the vertex being dragged

        self.cv = tk.Canvas(win, width=W, height=H, bg="#f2f7f7")
        self.cv.pack(side="left", padx=6, pady=6)
        self.cv.bind("<ButtonPress-1>", self.on_left_press)
        self.cv.bind("<B1-Motion>", self.on_left_drag)
        self.cv.bind("<ButtonRelease-1>", lambda e: setattr(self, "drag", None))
        self.cv.bind("<ButtonPress-3>", self.on_right_click)   # Windows / Linux
        self.cv.bind("<ButtonPress-2>", self.on_right_click)   # macOS

        panel = tk.Frame(win)
        panel.pack(side="left", fill="y", padx=6, pady=6)
        tk.Label(panel, text="Minimal sample length (epsilon):").pack(anchor="w")
        self.eps = tk.Scale(panel, from_=10, to=300, orient="horizontal",
                            length=200, command=lambda v: self.draw())
        self.eps.set(30)
        self.eps.pack()
        self.show_segpoly = tk.BooleanVar(value=False)
        tk.Checkbutton(panel, text="show control polygons of segments",
                       variable=self.show_segpoly, command=self.draw).pack(anchor="w", pady=6)
        self.info = tk.Label(panel, justify="left")
        self.info.pack(anchor="w", pady=10)

        self.visualize = tk.BooleanVar(value=False)
        tk.Checkbutton(panel, text="Visualize computations", variable=self.visualize,
                       command=self.draw).pack(anchor="w", pady=(120, 0))
        tk.Label(panel, text="t:").pack(anchor="w")
        self.t = tk.Scale(panel, from_=0, to=1, resolution=0.01, orient="horizontal",
                          length=200, command=lambda v: self.draw())
        self.t.set(0.5)
        self.t.pack()
        tk.Button(panel, text="Reset", width=22, pady=6, command=self.clear).pack(pady=14)
        self.draw()

    # ---------- mouse ----------
    def nearest(self, x, y):
        """Index of the control vertex closest to (x, y) within PICK_RADIUS, else None."""
        best, bd = None, PICK_RADIUS
        for i, p in enumerate(self.pts):
            d = math.dist(p, (x, y))
            if d <= bd:
                best, bd = i, d
        return best

    def on_left_press(self, e):
        i = self.nearest(e.x, e.y)
        if i is None:
            self.pts.append([e.x, e.y])      # new vertex
        else:
            self.drag = i                    # start moving an existing one
        self.draw()

    def on_left_drag(self, e):
        if self.drag is not None:
            self.pts[self.drag] = [e.x, e.y]
            self.draw()

    def on_right_click(self, e):
        i = self.nearest(e.x, e.y)
        if i is not None:
            del self.pts[i]
            self.draw()

    def clear(self):
        self.pts = []
        self.draw()

    # ---------- drawing ----------
    def line(self, poly, color, width=1):
        """Draw a polyline through the given points."""
        if len(poly) > 1:
            self.cv.create_line(*[c for p in poly for c in p], fill=color, width=width)

    def dot(self, p, r, color):
        self.cv.create_oval(p[0] - r, p[1] - r, p[0] + r, p[1] + r, fill=color, outline="")

    def draw_vector(self, p, d, color):
        """Line of fixed length 90 px from p in direction d (length only for display)."""
        length = math.hypot(*d)
        if length < 1e-9:
            return
        self.cv.create_line(p[0], p[1], p[0] + 90 * d[0] / length,
                            p[1] + 90 * d[1] / length, fill=color, width=2)

    def draw(self):
        self.cv.delete("all")
        pts, n = self.pts, len(self.pts) - 1

        # original control polygon
        self.line(pts, C_POLY)

        # adaptive refinement: the curve is the polyline through the end points of
        # the final segments (first point of the first, last point of every polygon)
        segments = adaptive_refine(pts, self.eps.get())
        if segments:
            self.line([segments[0][0]] + [s[-1] for s in segments], C_CURVE, 2)
        if self.show_segpoly.get():
            for s in segments:
                self.line(s, "#e67e22")

        # de Casteljau visualisation, point, tangent and normal
        if self.visualize.get() and n >= 1:
            rows = de_casteljau_rows(pts, self.t.get())
            for k in range(1, n):                 # rows 1 .. n-1 (row n is the point)
                self.line(rows[k], C_ROW)
            point = rows[n][0]
            # b'(t) = n * (b_1^{n-1} - b_0^{n-1}): direction of the last segment
            a, b = rows[n - 1][0], rows[n - 1][1]
            tangent = (b[0] - a[0], b[1] - a[1])
            self.draw_vector(point, tangent, C_TANGENT)
            self.draw_vector(point, (-tangent[1], tangent[0]), C_NORMAL)  # rotated by 90 deg
            self.dot(point, 4, C_POINT)

        # control vertices on top
        for p in pts:
            self.dot(p, 3, C_VERTEX)

        self.info.config(text="degree n = %d\nsegments: %d" % (max(n, 0), len(segments)))


if __name__ == "__main__":
    window = tk.Tk()
    App(window)
    window.mainloop()
