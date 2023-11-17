from __future__ import division
from matplotlib import collections  as mc
from branch import Branch
from leaf import Leaf
import matplotlib.patches as patches
import numpy as np
import math
import matplotlib.pyplot as plt
import time
import xml.etree.ElementTree as ET
from shapely.geometry import Polygon, Point
import re

#####################################PARAMETROS
cont=0
maxdis = 100
mindis = 5
apertura_max = 90.0
apertura_min = 30.0
grosor_max = 30.0
delta= 4 #coeficiente de variacion de apertura
#cant_puntos_inicial = 1000
sigma = 0.01 # coeficiente de convergencia
porcentaje_ocupacion=100.0 #el arbol va a crecer hasta ese porcentaje de ocupacion, dependiendo las leaves qe queden.
cant_converger = 20 #cant de iteraciones iguales para llegar a la convergencia
svg_utilizado = "leaf.svg"
porcentaje_sampleo = 25 #porcentaje de puntos de atraccion

#####################################ARCHIVO CON PUNTOS
puntos = np.array([])
f = open ("file.txt", "r")
for i in f:
  x = i.split(",")[0]
  y = i.split(",")[1]
  puntos=np.append(puntos, Leaf(float(x),float(y)))
cant = int(porcentaje_sampleo*len(puntos)/100)
puntos = puntos[:cant]
cant_puntos_inicial = len(puntos)
print(len(puntos))


#pos_global = np.array([50,2]) #ejemplo2
#pos_global = np.array([25,72])
#pos_global = np.array([70,75]) #star
#pos_global = np.array([86,270]) #arbolito
#pos_global =puntos[1].pos
pos_global = np.array([460,820]) #leaf
#pos_global = np.array([28.7,12]) #triangulo
#####################################CLASE TREE
class Tree:
  cont =0
  leaves = []
  branches = []
  contour = None
  def __init__(self):
    self.leaves = puntos.tolist()
    pos = pos_global
    dir = np.array([0,-1])
    root = Branch(None, pos, dir)
    self.branches.append(root)
    current = root
    found = False
    #extrae el path
    svg_path = self.parse_svg(svg_utilizado)
    #extrae el contorno a la imagen svg
    self.contour = self.extract_contour(svg_path)
    while not found:
      for i in range(len(self.leaves)):
        d = (current.pos-self.leaves[i].pos)[0]**2 + (current.pos-self.leaves[i].pos)[1]**2
        #d = np.linalg.norm(current.pos-self.leaves[i].pos)
        if d < maxdis**2:
        #if d < maxdis:
          found = True
      if not found:
        branch = current.next()
        current = branch
        self.branches.append(current);

  def fun_apertura(self,branch):
    aper = apertura_max - (delta * branch.get_depth())
    if (aper < apertura_min ):
      return apertura_min
    else:
      return aper

  def fun_apertura_automatico(self,branch,ocupacion_actual):
    aper = apertura_max - (ocupacion_actual/100) * apertura_max
    if (aper < apertura_min):
      return apertura_min
    else:
      return aper

  def converge (self, ocupacion_actual,ocupacion_anterior):
    if ((ocupacion_actual-ocupacion_anterior) <= sigma):
      self.cont = self.cont +1
      if(self.cont > cant_converger):
        return True
    else:
      self.cont =0
      return False
    return False

  def grow(self):
    iter = 0
    ocupacion_actual=0
    while ocupacion_actual < porcentaje_ocupacion:
      ocupacion_anterior = ocupacion_actual
      print("iter:", iter, " - leaves: ",len(self.leaves)," - branches: ",len(self.branches)," - porcentaje_ocupacion: ", ocupacion_actual)
      iter = iter+1
      for i in range(len(self.leaves)):
        if(self.leaves[i].reached == False):
          leaf = self.leaves[i]
          closestBranch = None
          record = maxdis**2
          for branch in self.branches:
            d = (leaf.pos-branch.pos)[0]**2 + (leaf.pos-branch.pos)[1]**2
            #d = np.linalg.norm(leaf.pos-branch.pos)
            if d < mindis**2:
            #if d < mindis:
              leaf.reachedM()
              closestBranch = None
              break
            elif d < record:
              f = branch.dir / np.linalg.norm(branch.dir)
              resta=np.subtract(leaf.pos, branch.pos)
              o = resta / np.linalg.norm(resta)
              c = np.array([f]).dot(o)
              rad = math.acos(float(round(c[0], 6)))
              grado = math.degrees(rad)
              #aper= self.fun_apertura_automatico(branch, ocupacion_actual)
              aper = self.fun_apertura(branch)
              if (grado < aper):
                closestBranch = branch
                record = d
        if closestBranch != None:
          newDir = np.subtract(leaf.pos, closestBranch.pos)
          newDir = newDir / np.linalg.norm(newDir)
          closestBranch.dir= np.add(closestBranch.dir,newDir)
          closestBranch.count = closestBranch.count+1
      for i in range(len(self.leaves)-1,-1,-1):
        if self.leaves[i].reached:
          self.leaves.pop(i)
      cant_leaves_ocupadas= cant_puntos_inicial - len(self.leaves)
      ocupacion_actual = (cant_leaves_ocupadas*100)/cant_puntos_inicial
      for i in range(len(self.branches)):
        if self.branches[i].count > 0:
          self.branches[i].dir = self.branches[i].dir/(self.branches[i].count+1)
          #para saber si esta dentro del contorno
          if self.dentro_contorno(np.add(self.branches[i].dir*self.branches[i].len, self.branches[i].pos)):
            sig_rama=self.branches[i].next()
            self.branches.append(sig_rama)
            self.branches[i].reset()
      if(self.converge(ocupacion_actual,ocupacion_anterior)):
        break

  def show(self):
    fx = np.array([])
    fy = np.array([])
    for i in range(len(self.leaves)):
      fx = np.append(fx, self.leaves[i].pos[0])
      fy = np.append(fy, self.leaves[i].pos[1])
    fig, ax = plt.subplots()
    x1 = np.array([])
    y1 = np.array([])
    x2 = np.array([])
    y2 = np.array([])
    lines = []
    grosores = []
    # Create a Polygon patch for the shadow
    shadow_polygon = patches.Polygon(self.contour, closed=True, edgecolor='none', facecolor='#000000',alpha=0.10)
    # Add the shadow polygon to the plot
    ax.add_patch(shadow_polygon)
    for i in range(1, len(self.branches)):
      if self.branches[i].parent is not None:
        p = [(self.branches[i].pos[0], self.branches[i].pos[1]),
             (self.branches[i].parent.pos[0], self.branches[i].parent.pos[1])]
        lines.append(p)
        #grosores.append(grosor_dibujo / self.branches[i].get_depth())
        grosores.append(self.branches[i].grosor)
        print("grosores: ", self.branches[i].grosor)
        x1 = np.append(x1, self.branches[i].pos[0])
        y1 = np.append(y1, self.branches[i].pos[1])
        x1 = np.append(x1, self.branches[i].parent.pos[0])
        y1 = np.append(y1, self.branches[i].parent.pos[1])
    plt.scatter(x1, y1, color='#900040', s=0.001)
    #lc = mc.LineCollection(lines, colors='#900040', linewidths=2, alpha=0.7)
    grosores= grosores/np.linalg.norm(grosores)*grosor_max
    print("grosoresnorm:", grosores)
    lc = mc.LineCollection(lines, colors='#900040', linewidths=grosores, alpha=0.7)
    ax.add_collection(lc)
    ax.set_axis_off()
    plt.tight_layout()
    plt.show()

  #extrae el path
  def parse_svg(self,svg_file):
      tree = ET.parse(svg_file)
      root = tree.getroot()
      # Assuming the first path element in the SVG represents the contour
      path_data = root.find(".//{http://www.w3.org/2000/svg}path").get("d")
      return path_data

  # Step 2: Extract contour coordinates from the SVG path
  def extract_contour(self,svg_path):
      # Extract all numeric values from the path data using regular expressions
      coordinates = [float(coord) for coord in re.findall(r'-?\d+\.\d+', svg_path)]
      # Separate x and y coordinates
      x_coords = coordinates[::2]
      y_coords = coordinates[1::2]
      # Create a list of tuples for the coordinates
      contour_coords = list(zip(x_coords, y_coords))
      return contour_coords

  def dentro_contorno(self, branch):
    contour_polygon = Polygon(self.contour)
    point = Point(branch[0],branch[1])
    return contour_polygon.contains(point)

#####################################GROW + SHOW
tree = Tree()
start = time.time()
tree.grow()
end = time.time()
print("tiempo del grow: ", end - start)
tree.show()