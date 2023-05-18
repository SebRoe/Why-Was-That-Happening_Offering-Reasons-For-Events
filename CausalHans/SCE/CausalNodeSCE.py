from anytree import Node, RenderTree, NodeMixin, Resolver, PostOrderIter, PreOrderIter
from anytree.exporter import DotExporter
from anytree.dotexport import RenderTreeGraph
import os, uuid 
from Utils.logger import get_spec_logger

logger = get_spec_logger(__name__)


def nodenamefuncSCE(node):
    use_uuid = os.environ.get("USE_UUID", "True") == "True"
    name = f"{node.name}\n"

    if node.indicator is not None:
        name += f"{str(node.indicator)}\n"
    if use_uuid:
        name += f"{str(node.uuid)}"

    return name 



class CausalNodeSCE(NodeMixin):

    def __init__(self, name, causalParent=None, causalChild=None, muParent=None, muChild=None, valueParent=None, valueChild=None, parent=None, children=None, indicator=None, **kwargs):
        super().__init__()
        self.name = name
        self.parent = parent
        self.indicator = indicator
        self.causalParent = causalParent
        self.causalChild = causalChild
        self.muParent = muParent
        self.muChild = muChild
        self.valueParent = valueParent
        self.valueChild = valueChild
        self.__dict__.update(kwargs)
        self.uuid = uuid.uuid4()
        if children:
            self.children = children

    def __repr__(self):
        return f"{self.name}"

    def __str__(self):
        return f"{self.name}"




