from anytree import Node, RenderTree, NodeMixin, Resolver, PostOrderIter, PreOrderIter
from anytree.exporter import DotExporter
from anytree.dotexport import RenderTreeGraph
import os, uuid 
from Utils.logger import get_spec_logger


    




### Tree Building Helper Functions  
def find_sequences(node:Node):

    cRoot = node.root 
    cNodes = [cNode for cNode in PreOrderIter(cRoot)]
    cVariables = list(set([cNode.name for cNode in cNodes]))

    cSequencesPerVariable = [] 
    for cVariable in cVariables:
        cNodesByVariable = [cNode for cNode in cNodes if cNode.name == cVariable]
        cNodesByVariable = [cNode for cNode in cNodesByVariable if not cNode.is_leaf]
        cNodesByVariable.sort(key=lambda x: x.timestepCausalChild, reverse=True)

        # print([(cNode.name, cNode.is_leaf) for cNode in cNodesByVariable])
        # print([(cNode.children, cNode.timestepChild) for cNode in cNodesByVariable])
        # print("\n")

        cSequence = []
        cSequenceUUID = str(uuid.uuid4())
        cIndicators = {}
        for cNode in cNodesByVariable:

            # cSequence.append(cNode)
            # cSequencesPerVariable.append((cSequenceUUID, cSequence))

            # cSequence = []
            # cSequenceUUID = str(uuid.uuid4())

            if cIndicators == {}:
                for cChild in cNode.children:
                    cIndicators["child_" + cChild.name] = cChild.indicator 
                cSequence.append(cNode)
                
            else:
                cMismatched = False 
                for cChild in cNode.children:
                    if cIndicators["child_" + cChild.name] != cChild.indicator:
                        cMismatched = True 
                        break
                    else:
                        cSequence.append(cNode)

                if cMismatched:
                    if cSequence != []:
                        cSequencesPerVariable.append((cSequenceUUID, cSequence))
                    cIndicators = {}
                    cSequence = []
                    for cChild in cNode.children:
                        cIndicators["child_" + cChild.name] = cChild.indicator
                    cSequenceUUID = str(uuid.uuid4())
                    cSequence.append(cNode)

        if cSequence != []: 
            cSequencesPerVariable.append((cSequenceUUID, cSequence))

    for cSequenceUUID, cSequence in cSequencesPerVariable:
        for cNode in cSequence:
            cNode.sequenceTag = cSequenceUUID

    return cSequencesPerVariable
