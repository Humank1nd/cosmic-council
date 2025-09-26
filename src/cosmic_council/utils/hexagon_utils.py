# Code structure remains similar, only the calculation of sub_center coordinates
# and sub_side_length needs adjustment.

# ... (imports, setup screen, setup turtle - remain the same)

# --- Function to Draw a Complete Hexagon Figure (Outline + Dividing Lines) ---
# This function remains exactly the same as before
def draw_complete_hexagon(t, center_x, center_y, side):
    """Draws a hexagon outline and its 6 dividing lines centered at (cx, cy)."""
    if side < 1: # Stop if shapes get too small
        return

    # Calculate vertices relative to the center (cx, cy)
    vertices = []
    for i in range(6):
        # Standard orientation: vertex at angle 0 (positive x-axis relative to center)
        angle_deg = 60 * i
        angle_rad = math.radians(angle_deg)
        vx = center_x + side * math.cos(angle_rad)
        vy = center_y + side * math.sin(angle_rad)
        vertices.append((vx, vy))

    # Draw hexagon outline
    t.penup()
    t.goto(vertices[0]) # Go to the first vertex
    t.pendown()
    for i in range(1, 6):
        t.goto(vertices[i])
    t.goto(vertices[0]) # Close the hexagon
    t.penup()

    # Draw dividing lines from center to vertices
    t.goto(center_x, center_y)
    t.pendown()
    for vx, vy in vertices:
        t.goto(vx, vy)
        t.goto(center_x, center_y) # Go back to center
    t.penup()


# --- Main Drawing Logic ---
try:
    # 1. Draw the main, large hexagon centered at (0, 0)
    print(f"Drawing main hexagon: Center=(0, 0), Side={INITIAL_SIDE_LENGTH}")
    draw_complete_hexagon(pen, 0, 0, INITIAL_SIDE_LENGTH)

    # 2. Calculate size and centers for the smaller hexagons to fit inside each sector triangle
    # Max side length for hexagon inside equilateral triangle of side L is L/3
    small_side_length = INITIAL_SIDE_LENGTH / 3.0

    # Centroid of sector triangle is distance L/sqrt(3) from origin (0,0)
    # along the angle bisector of the sector (angle + 30 deg)
    dist_to_centroid = INITIAL_SIDE_LENGTH / math.sqrt(3.0)

    for i in range(6):
        # Angle to the centroid (midpoint angle of the sector)
        angle_deg = 60 * i + 30
        angle_rad = math.radians(angle_deg)

        # Calculate the center coordinates for the smaller hexagon (centroid of the sector triangle)
        sub_center_x = dist_to_centroid * math.cos(angle_rad)
        sub_center_y = dist_to_centroid * math.sin(angle_rad)

        print(f"Drawing inner hexagon {i+1}: Center=({sub_center_x:.1f}, {sub_center_y:.1f}), Side={small_side_length:.1f}")
        # 3. Draw the smaller hexagon figure centered at the centroid
        draw_complete_hexagon(pen, sub_center_x, sub_center_y, small_side_length)


    screen.update() # Update screen now that drawing is complete

# --- Keep Window Open ---
    print("\nDrawing complete. Click the window to close.")
    screen.exitonclick()

except turtle.Terminator:
    print("Turtle window closed.")
except Exception as e:
    print(f"An error occurred: {e}")