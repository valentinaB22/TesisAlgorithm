import numpy as np

class Branch:
  count = 0
  parent=None
  pos=None
  dir=None
  origDir=None
  def __init__(self, parent, pos, dir):
    self.pos = pos
    self.parent = parent
    self.dir = dir
    self.origDir = self.dir#.copy()
    self.count = 0
    self.len = 2 #####################LONGITUD DE LA RAMA

  def reset(self):
      self.dir = self.origDir#.copy()
      self.count = 0

  def next(self):
    nextDir = self.dir * self.len
    nextPos = np.add(self.pos, nextDir)
    nextBranch = Branch(self, nextPos, self.dir)#.copy())
    return nextBranch