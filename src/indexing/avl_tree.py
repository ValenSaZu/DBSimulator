from typing import Optional, Any

class Node:
    def __init__(self, value, address: Optional[tuple] = None):
        self.value = value
        self.address = address  # (sector, offset)
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
  def ins(self, p, x, address: Optional[tuple] = None):
    if not p:
      return Node(x, address)
    if x < p.value:
      p.left = self.ins(p.left, x, address)
    elif x > p.value:
      p.right = self.ins(p.right, x, address)
    else:
      p.address = address
      return p

    return self.balance(p)

  def insert(self, x, address: Optional[tuple] = None):
    self.root = self.ins(self.root, x, address)

  def search(self, x) -> Optional[Node]:
    # Busca un valor en el árbol AVL
    return self._search_recursive(self.root, x)
  
  def _search_recursive(self, node: Optional[Node], x: Any) -> Optional[Node]:
    # Búsqueda recursiva en el árbol
    if node is None or node.value == x:
      return node
    
    if x < node.value:
      return self._search_recursive(node.left, x)
    else:
      return self._search_recursive(node.right, x)

  def inorder(self, p):
    if p:
      self.inorder(p.left)
      print(f"{p.value} (address: {p.address})", end=" ")
      self.inorder(p.right)
  
  def get_all_nodes(self) -> list:
    # Obtiene todos los nodos del árbol en orden
    nodes = []
    self._inorder_collect(self.root, nodes)
    return nodes
  
  def _inorder_collect(self, node: Optional[Node], nodes: list):
    if node:
      self._inorder_collect(node.left, nodes)
      nodes.append(node)
      self._inorder_collect(node.right, nodes)

  def from_records(self, records: list):
    # Inserta múltiples registros en el árbol AVL
    for record in records:
      sector = record.get('sector')
      offset = record.get('offset')
      primary_key = record[self.schema['primary_key']]
      self.insert(primary_key, (sector, offset))
  
  def get_data_from_node(self, node: Node):
    sector_address, offset = node.address
    data = self.sector_manager.read_record(sector_address, offset)
    return data