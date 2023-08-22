import numpy as np

class Leaf:
  reached=False

  def __init__(self, x,y):
    self.pos = np.array([x,y])
    self.reached = False

  def reachedM(self):
    self.reached = True