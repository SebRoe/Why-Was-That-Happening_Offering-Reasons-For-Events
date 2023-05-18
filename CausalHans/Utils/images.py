import os, time, uuid  
from anytree import Node, RenderTree, NodeMixin, Resolver, PostOrderIter, PreOrderIter
from anytree.exporter import DotExporter
from anytree.dotexport import RenderTreeGraph


def getDynDirImg(filename:str):
    return os.path.join("..", "img", "dynamic", filename)


def getTimeAsString():
    return str(int(time.time()))


### Plotting Helper Functions 
def nodenamefuncTSCE(node):
    use_uuid = os.environ.get("USE_UUID", "True") == "True"
    name = f"{node.name}\n"

    if node.timestepCausalChild is not None:
        name += f"t={node.timestepCausalParent}\n"
    if node.indicator is not None:
        name += f"ind={str(node.indicator)}\n"
 
    #if node.sequenceTag is not None:
    #    name += f"seqID={node.sequenceTag}\n"

    # try:
    #     muParent = node.__dict__['muParent']
    #     valueParent = node.__dict__['valueParent']

    #     if muParent > valueParent:
    #         name += f"LOW\n"

    #     elif muParent < valueParent:
    #         name += f"HIGH\n"
    # except:
    #     pass 

    if use_uuid:
       name += f"uuid={str(node.uuid)}\n"
    return name 


def nodeattrfuncDynamicTSCE(node):

    if node.is_leaf:
        return f'shape=box, color="#000000"'
    else:
        try:
            cSeqUUID = node.sequenceTag
            if cSeqUUID is None:
                print(node.name + " has no causal sequence UUID", node.timestepCausalChild)
                return f'shape=box, color=red'
            hashed_uuid = uuid.uuid5(uuid.NAMESPACE_URL, cSeqUUID).hex
            r, g, b = int(hashed_uuid[:2], 16), int(hashed_uuid[2:4], 16), int(hashed_uuid[4:6], 16)
            color_code = "#{:02x}{:02x}{:02x}".format(r, g, b)
            return f'shape=box, color="{color_code}"'
        
        except:
            cSeqUUID = node.causalSequenceUUID
            if cSeqUUID is None:
                print(node.name + " has no causal sequence UUID", node.timestepCausalChild)
                return f'shape=box, color=red'
            hashed_uuid = uuid.uuid5(uuid.NAMESPACE_URL, cSeqUUID).hex
            r, g, b = int(hashed_uuid[:2], 16), int(hashed_uuid[2:4], 16), int(hashed_uuid[4:6], 16)
            color_code = "#{:02x}{:02x}{:02x}".format(r, g, b)
            return f'shape=box, color="{color_code}"'


def generateTreeImageSCE(sce_root, nodenamefuncSCE ,filepath):
    RenderTreeGraph(sce_root, nodenamefunc=nodenamefuncSCE).to_picture(filepath)

def generateTreeImage(rootNode:Node, filepath):
    RenderTreeGraph(rootNode, nodenamefunc=nodenamefuncTSCE, nodeattrfunc=nodeattrfuncDynamicTSCE).to_picture(filepath)




























@DeprecationWarning
def flatten(l):
    # flatten any complicatedly nested list to its literals
    for el in l:
        if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el

@DeprecationWarning
class Rlist:
    """A recursive list consisting of a first element and the rest."""
    class EmptyList(object):

        def __str__(self):
            return "(#)"

        def __len__(self):
            return 0

    empty = EmptyList()

    def __init__(self, first, rest=empty):
        self.first = first
        self.rest = rest

    def __getitem__(self, i):
        if i == 0:
            return self.first
        else:
            return self.rest[i-1]

    def __len__(self):
        return 1 + len(self.rest)
    
    
    def __str__(self):
        """Return a pretty string representation of this Rlist."""
        repr = str(self.first) + " -> "
        if isinstance(self.rest, list):
            repr += "["
            len_rest = len(self.rest)
            for i, r in enumerate(self.rest):
                repr +=   str(r)
                if i < len_rest - 1:
                    repr += ", "

            repr += "]"
        elif isinstance(self.rest, self.EmptyList):
            repr += "[" + str(self.rest) + "]" 

        return repr

        
    def print_as_tree(self, depth=0):
        """Print the Rlist as a tree."""
        print(" " * depth + str(self.first))
        if isinstance(self.rest, list):
            for r in self.rest:
                r.print_as_tree(depth + 3)
        elif isinstance(self.rest, self.EmptyList):
            print(" " * (depth + 3) + str(self.rest))
        else:
            self.rest.print_as_tree(depth + 3)

    def pprint(self, depth=0):
        first = self.first 
        rest = self.rest

        if isinstance(first, list):
            for idx, element in enumerate(first):
                print(" " * (depth) + str(element))
                if isinstance(rest, self.EmptyList):
                    pass
                else:
                    rest[idx].pprint(depth + 5)
        




