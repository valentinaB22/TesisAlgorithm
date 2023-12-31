from __future__ import division
from matplotlib import collections  as mc
from branch import Branch
from leaf import Leaf
import numpy as np
import math
import matplotlib.pyplot as plt

#####################################PARAMETROS
maxdis = 40
mindis = 2
angulo_min = 0.0
angulo_max = 90.0

#####################################ARCHIVO CON PUNTOS
puntos = np.array([])
f = open ("ejemplo2.txt", "r")
for i in f:
  x = i.split(",")[0]
  y = i.split(",")[1]
  puntos=np.append(puntos, Leaf(float(x),float(y)))
puntos = puntos[:10]
print(len(puntos))

#####################################CLASE TREE
class Tree:
  leaves = []
  branches = []
  def __init__(self):
    self.leaves = puntos.tolist()
    pos = np.array([50,0])
    dir = np.array([0, -1])
    root = Branch(None, pos, dir)
    self.branches.append(root)
    current = root
    found = False
    while not found:
      for i in range(len(self.leaves)):
        d = (current.pos-self.leaves[i].pos)[0]**2 + (current.pos-self.leaves[i].pos)[1]**2
        if d < maxdis**2:
          found = True
      if not found:
        branch = current.next()
        current = branch
        self.branches.append(current);

  def grow(self):
    iter = 50
    while iter > 0:
      print("iter:", iter, " - leaves: ",len(self.leaves)," - branches: ",len(self.branches))
      iter = iter-1
      for i in range(len(self.leaves)):
        if(self.leaves[i].reached == False):
          leaf = self.leaves[i]
          closestBranch = None
          record = maxdis**2
          for branch in self.branches:
            d = (leaf.pos-branch.pos)[0]**2 + (leaf.pos-branch.pos)[1]**2
            #d = np.linalg.norm(leaf.pos-branch.pos);
            if d < mindis**2:
              leaf.reachedM()
              closestBranch = None
              break
            elif d < record:
              grado = math.degrees(math.atan2(leaf.pos[1]-branch.pos[1],leaf.pos[0]-branch.pos[0])) % 360
              if((grado > angulo_min) & (grado < angulo_max)):
                closestBranch = branch
                record = d
        if closestBranch != None:
          newDir = np.subtract(leaf.pos, closestBranch.pos)
          newDir = newDir / np.linalg.norm(newDir)
          closestBranch.dir   = np.add(closestBranch.dir,newDir)
          closestBranch.count = closestBranch.count+1
      for i in range(len(self.leaves)-1,-1,-1):
        if self.leaves[i].reached:
          self.leaves.pop(i)
      for i in range(len(self.branches)):
        if self.branches[i].count > 0:
          self.branches[i].dir = self.branches[i].dir/(self.branches[i].count+1)
          sig_rama=self.branches[i].next()
          self.branches.append(sig_rama)
          self.branches[i].reset()

  def show(self):
    fx =np.array([])
    fy =np.array([])
    for i in range(len(self.leaves)):
      fx=np.append(fx,self.leaves[i].pos[0])
      fy=np.append(fy,self.leaves[i].pos[1])
    fig, ax = plt.subplots()
    x1 =np.array([])
    y1 =np.array([])
    x2 =np.array([])
    y2 =np.array([])
    lines = []
    for i in range(1,len(self.branches)):
      if self.branches[i].parent != None:
        p = [(self.branches[i].pos[0], self.branches[i].pos[1]), (self.branches[i].parent.pos[0], self.branches[i].parent.pos[1])]
        lines.append(p)
        x1=np.append(x1,self.branches[i].pos[0])
        y1=np.append(y1,self.branches[i].pos[1])
        x1=np.append(x1,self.branches[i].parent.pos[0])
        y1=np.append(y1,self.branches[i].parent.pos[1])
    plt.scatter(x1, y1)
    lc = mc.LineCollection(lines, colors='red', linewidths=1)
    ax.add_collection(lc)
    plt.grid(True)
    plt.tight_layout()
    plt.scatter(fx,fy)
    plt.show()

#####################################GROW + SHOW
tree = Tree()
tree.grow()
tree.show()