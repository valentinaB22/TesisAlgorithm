import numpy as np

class Branch:
  count = 0
  parent=None
  pos=None
  dir=None
  origDir=None
  depth = 1
  grosor = 1

  def __init__(self, parent, pos, dir):
    self.pos = pos
    self.parent = parent
    self.dir = dir
    self.origDir = self.dir
    self.count = 0
    self.len = 5 ####################LONGITUD DE LA RAMA
    if parent:
      self.depth= parent.get_depth()+1
      self.parent.incrementar_grosor()

  def incrementar_grosor(self):
    self.grosor = self.grosor + 1
    if self.parent:
      self.parent.incrementar_grosor()

  def get_depth(self):
    return self.depth

  def reset(self):
      self.dir = self.origDir
      self.count = 0

  def next(self):
    nextDir = self.dir * self.len
    nextPos = np.add(self.pos, nextDir)
    nextBranch = Branch(self, nextPos, self.dir)
    return nextBranch