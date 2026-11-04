# Bézier Curve — Programming Assignment 1

**Course:** Modelling of Curves and Surfaces (1)  
**Topic:** Bézier Curve  
**Language:** Python 3  
**GUI:** Tkinter  
**Dependencies:** Python standard library only

## 1. Project overview

This application demonstrates a Bézier curve defined by a sequence of control points.

The user can add, move and delete control points. The program redraws the curve approximation after every change. It uses adaptive refinement: a Bézier segment is subdivided at `t = 1/2` while at least one edge of its control polygon has length greater than or equal to epsilon.

The application can also visualize the de Casteljau construction for a user-selected parameter `t`, including the point on the curve, tangent and normal vectors.

## 2. Requirements

- Python 3.8 or newer.
- Tkinter, which is included with most standard Python installations.
- No third-party Python packages are required.

On some Linux installations, Tkinter may need to be installed separately by the operating system package manager.

## 3. How to run

Open a terminal in the folder containing `main.py`.

**Windows:**

```powershell
py main.py
```

**macOS / Linux:**

```bash
python3 main.py
```

## Application Screenshot

![Bézier Curve Application](img.png)

## 4. How to use the application

1. Left-click an empty part of the canvas to add a control point.
2. Left-click a control point and drag it to change its position.
3. Right-click a control point to delete it.
4. Move the **Epsilon** slider to change the maximum allowed edge length.
5. Select **Show refined control polygons** to display the control polygons of the final subcurves.
6. Select **Show de Casteljau construction** to display the interpolation rows, curve point, tangent and normal.
7. Move the **t** slider to change the parameter used for the de Casteljau construction.
8. Press **Reset / clear points** to remove all control points.

## 5. Mathematical concepts

### Bézier curve

A Bézier curve of degree `n` is defined by control points `P0, P1, ..., Pn`. Its parameter is `t` in the interval `[0, 1]`.

For a cubic curve:

\[
B(t)=(1-t)^3P_0+3(1-t)^2tP_1+3(1-t)t^2P_2+t^3P_3.
\]

The curve starts at the first control point and ends at the last control point. The intermediate control points influence its shape.

### de Casteljau algorithm

The algorithm repeatedly interpolates between neighbouring points:

\[
b_i^k(t)=(1-t)b_i^{k-1}(t)+t b_{i+1}^{k-1}(t).
\]

The final point is `B(t)`. The application stores all rows so they can be drawn on the canvas.

### Subdivision at the midpoint

For adaptive refinement, the curve is split at `t = 1/2`. The first point of each de Casteljau row forms the left subcurve's control points. The last point of each row, read in reverse row order, forms the right subcurve's control points.

### Adaptive refinement and epsilon

A control polygon is subdivided if at least one neighbouring pair satisfies:

\[
\|P_{i+1}-P_i\|\geq\varepsilon.
\]

Subdivision continues until all edges of a final control polygon are shorter than epsilon, subject to a recursion safety limit in the implementation.

- Smaller epsilon generally produces more subdivisions.
- Larger epsilon generally produces fewer subdivisions.
- The slider has a minimum value of 10.

The curve approximation is drawn by connecting the endpoints of the final refined segments. The final control polygons can also be displayed.

### Tangent and normal

For a degree `n` Bézier curve, the derivative direction is calculated from the last two de Casteljau rows:

\[
B'(t)=n\left(b_1^{n-1}(t)-b_0^{n-1}(t)\right).
\]

A normal direction is obtained by rotating the tangent vector `(x, y)` to `(-y, x)`. The displayed arrows are scaled to a fixed screen length for visibility.

## 6. Main source-code structure

| Function / class | Responsibility |
|---|---|
| `interpolate` | Linear interpolation between two points |
| `de_casteljau` | Calculates and returns all de Casteljau rows |
| `subdivide_at_half` | Splits a Bézier curve at `t = 1/2` |
| `has_edge_at_least_epsilon` | Checks the assignment's edge-length condition |
| `refine_curve` | Recursively subdivides the curve |
| `bezier_tangent` | Calculates the tangent vector |
| `BezierApplication` | Creates the GUI and handles user interaction and drawing |

## 7. Suggested presentation order

1. Introduce the purpose of the application and the control points.
2. Demonstrate adding, moving and deleting points.
3. Explain the control polygon and the Bézier curve approximation.
4. Change epsilon and explain why the number of refined segments changes.
5. Enable the de Casteljau construction and move `t` from 0 to 1.
6. Identify the curve point, tangent and normal.
7. Explain how the code separates geometry calculations from the Tkinter interface.

## 8. Important implementation note

The recursive refinement function has a maximum recursion depth of 24 as a safety limit. If this limit is reached, a segment is returned even if an edge is still at least epsilon. For ordinary canvas-sized inputs and the provided epsilon range, this limit is intended to prevent excessive recursion.

The approximation method follows the assignment's specified control-polygon edge-length subdivision condition. It is not a separate flatness-error test.
