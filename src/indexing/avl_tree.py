class Node:
  def __init__(self, value):
    self.value = value
    self.left = None
    self.right = None
    self.height = 1

class AVL:
  def __init__(self):
    self.root = None

  def height(self, p):
    return p.height if p else 0

  def update_height(self, p):
    p.height = 1 + max(self.height(p.left), self.height(p.right))

  def balance_factor(self, p):
    return self.height(p.left) - self.height(p.right)

  # ----------------------- Rotaciones -----------------------
  def rotate_right(self, y):
    x = y.left
    T2 = x.right

    x.right = y
    y.left = T2

    self.update_height(y)
    self.update_height(x)
    return x

  def rotate_left(self, x):
    y = x.right
    T2 = y.left

    y.left = x
    x.right = T2

    self.update_height(x)
    self.update_height(y)
    return y

  # ----------------------- Balanceo -----------------------
  def balance(self, p):
    self.update_height(p)
    bf = self.balance_factor(p)

    # LL
    if bf > 1 and self.balance_factor(p.left) >= 0:
      return self.rotate_right(p)

    # RR
    if bf < -1 and self.balance_factor(p.right) <= 0:
      return self.rotate_left(p)

    # LR
    if bf > 1 and self.balance_factor(p.left) < 0:
      p.left = self.rotate_left(p.left)
      return self.rotate_right(p)

    # RL
    if bf < -1 and self.balance_factor(p.right) > 0:
      p.right = self.rotate_right(p.right)
      return self.rotate_left(p)

    return p

  # ----------------------------------------------
  def ins(self, p, x):
    if not p:
      return Node(x)
    if x < p.value:
      p.left = self.ins(p.left, x)
    elif x > p.value:
      p.right = self.ins(p.right, x)
    else:
      return p

    return self.balance(p)

  def insert(self, x):
    self.root = self.ins(self.root, x)

  def inorder(self, p):
    if p:
      self.inorder(p.left)
      print(p.value, end=" ")
      self.inorder(p.right)

def main():
  t = AVL()
  t.insert(10)
  t.insert(30)
  t.insert(20)

  t.inorder(t.root)

if __name__ == "__main__":
  main()