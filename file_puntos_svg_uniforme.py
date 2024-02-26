import math
import subprocess
import time

import svgwrite
import random
import xml.etree.ElementTree as ET

from matplotlib import pyplot as plt
from shapely.geometry import Polygon, Point
import re

# Step 1: Parse the SVG file to extract the contour information
def parse_svg(svg_file):
    tree = ET.parse(svg_file)
    root = tree.getroot()
    # Assuming the first path element in the SVG represents the contour
    path_data = root.find(".//{http://www.w3.org/2000/svg}path").get("d")
    return path_data

# Step 2: Extract contour coordinates from the SVG path
def extract_contour(svg_path):
    # Extract all numeric values from the path data using regular expressions
    coordinates = [float(coord) for coord in re.findall(r'-?\d+\.\d+', svg_path)]
    # Separate x and y coordinates
    x_coords = coordinates[::2]
    y_coords = coordinates[1::2]
    # Create a list of tuples for the coordinates
    contour_coords = list(zip(x_coords, y_coords))
    return contour_coords

# Step 3: Generate random points inside the contour
import numpy as np


def distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def generate_points_inside_contour_with_blue_noise(contour, num_points, num_candidates):
    contour_polygon = Polygon(contour)
    points_inside = []

    def score(candidate, existing_points):
        return min([Point(candidate).distance(Point(p)) for p in existing_points]) if existing_points else 0

    def generate_candidates(num_candidates):
        return [(random.uniform(min(x for x, y in contour), max(x for x, y in contour)),
                 random.uniform(min(y for x, y in contour), max(y for x, y in contour))) for _ in range(num_candidates)]

    while len(points_inside) < num_points:
        candidate_points = generate_candidates(num_candidates)
        candidate_points_inside = [p for p in candidate_points if contour_polygon.contains(Point(p))]

        if not candidate_points_inside:
            continue  # Skip iteration if no candidates are inside the contour

        scores = [score(candidate, points_inside) for candidate in candidate_points_inside]
        best_candidate_inside = candidate_points_inside[scores.index(max(scores))]
        points_inside.append(best_candidate_inside)

    return points_inside



def save_svg_with_points(svg_file, points_inside, output_file):
    # Load the SVG file
    drawing = svgwrite.Drawing(svg_file)
    # Extract the path data from the SVG
    path_data = parse_svg(svg_file)
    # Add the path to the SVG
    drawing.add(svgwrite.path.Path(d=path_data, fill="none", stroke="black"))
    # Add points inside the contour to the SVG
    for point in points_inside:
        x, y = point
        drawing.add(svgwrite.shapes.Circle(center=(x, y), r=1, fill="red"))
    # Save the SVG image
    drawing.saveas(output_file)

############################################# Main function
start = time.time()

svg_file = "star.svg"
num_points = 50
output_file = "prueba_star_50.svg"  # Specify the output file path
# Step 1: Parse the SVG and extract contour coordinates
svg_path = parse_svg(svg_file)
contour = extract_contour(svg_path)
# Step 2: Generate random points inside the contour
points_inside = generate_points_inside_contour_with_blue_noise(contour,num_points,50)
print(f"Generated {len(points_inside)} points inside the contour.")
# Step 3: Save the SVG image with points inside the contour
save_svg_with_points(svg_file, points_inside, output_file)
# Step 4: Display the saved SVG image using an external viewer (e.g., web browser)
subprocess.Popen(["open", output_file])
# Open a file for writing (creates the file if it doesn't exist)
with open("pruebastar_metricas_50.txt", "w") as file:
    for point in points_inside:
        x, y = point
        file.write(f"{x},{y},\n")
end = time.time()
print("tiempo de sampleo: ", end - start)
print(contour)
x_contour, y_contour = zip(*contour)
x_blue, y_blue = zip(*points_inside)

plt.plot(x_contour + (x_contour[0],), y_contour + (y_contour[0],), linestyle='-', color='black')
plt.scatter(x_blue, y_blue, marker='.', color='#900040')
plt.title('Blue Noise Sampling Inside a Polygon Contour')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.legend()
plt.show()