from anytree import Node, RenderTree, NodeMixin, Resolver, PostOrderIter, PreOrderIter
from anytree.exporter import DotExporter
from anytree.dotexport import RenderTreeGraph
from anytree.search import findall_by_attr
from .tree_helper import * 



class CausalNodeDynamicTSCE(NodeMixin): 
    def __init__(self, name, causalParent=None, causalChild=None,
                timestepCausalParent=None, timestepCausalChild=None, valueCausalParent=None, 
                valueCausalChild=None, parent=None, children=None, indicator=None,
                causalContext=None, transitionContext=None,  **kwargs):
        
        super().__init__()
        self.name = name
        self.parent = parent
        self.indicator = indicator
        self.causalParent = causalParent
        self.causalChild = causalChild
        self.timestepCausalParent = timestepCausalParent
        self.timestepCausalChild = timestepCausalChild
        self.valueCausalParent = valueCausalParent
        self.valueCausalChild = valueCausalChild
        self.causalSequenceUUID = None 
        self.relationStrength = None 
        self.__dict__.update(kwargs)
        self.uuid = uuid.uuid4()
        self.causalContext = str(causalContext)
        self.transitionContext = transitionContext 
        if children:
            self.children = children
        else:
            self.children = []
        
        if parent:
            self.parent = parent 
        else:
            self.parent = None 

    def addAttr(self, name, value):
        setattr(self, name, value)

    def hasAttr(self, name):
        return name in self.__dict__

    def hasGetAttr(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            return -1

    def __repr__(self):
        return f"{self.name}"

    def __str__(self):
        return f"{self.name}"
    

    def contains(self, node:Node):
        return node in self.descendants
    

    def containsSimilar(self, node:Node):
        exclude_attrs = ["uuid", "children"]
        for cNode in self.descendants:
            if all([getattr(cNode, attr) == getattr(node, attr) for attr in node.__dict__ if attr not in exclude_attrs]):
                return True
        return False
    

    def containsSimilarSubTree(self, node:Node):
        include_attrs = ["timestepCausalChild", "causalContext", "timestepCausalParent"]
        cRoot = self.root 
        cSameNamedNodes = findall_by_attr(cRoot, node.name, "name")
        for cNode in cSameNamedNodes:

            if node == cNode:
                continue 

            attributes_same = True 
            for attr in include_attrs:
                if getattr(cNode, attr) != getattr(node, attr):
                    attributes_same = False

            if attributes_same:
                return True

        return False 
            

    def getTreeDepth(node):
        return max([node.depth for node in PreOrderIter(node.root)])
    

    def getPathToRoot(self):
        return [node.name for node in self.path]
    

    # Deprecated
    def containsEqualSubTree(self, node:Node):
        root = self.root 
        for cNode in PreOrderIter(root):
            if self.somehowEqual(cNode, dropAttrs=["uuid", "parent"]):
                cNodeChildren = cNode.children
                for cNodeChild in cNodeChildren:
                    if node.somehowEqual(cNodeChild, dropAttrs=["uuid"]):
                        return True 
        return False

    # Deprecated
    def somehowEqual(self, node2, dropAttrs=[]):
        if all([getattr(self, attr) == getattr(node2, attr) for attr in self.__dict__ if attr not in dropAttrs and not attr.startswith("_")]) and self != node2:
            return True 
        else:
            return False 