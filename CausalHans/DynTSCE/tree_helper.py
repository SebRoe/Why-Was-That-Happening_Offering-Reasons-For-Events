from anytree import Node, RenderTree, NodeMixin, Resolver, PostOrderIter, PreOrderIter
from anytree.exporter import DotExporter
from anytree.dotexport import RenderTreeGraph
from anytree.search import findall_by_attr
import os, uuid 


### Helper functions to plot the tree 

def nodenamefuncDynamicTSCE(node):
    use_uuid = os.environ.get("USE_UUID", "True") == "True"
    name = f"{node.name}\n"
    name += f"tsP: {node.timestepCausalParent}\n"
    name += f"tsC: {node.timestepCausalChild}\n"
    name += f"ind: {node.indicator}\n"
    name += f"cc: {node.causalContext}\n"
    name += f"strength: {node.relationStrength}\n"
    if use_uuid:
        name += f"{str(node.uuid)}\n"
    return name

def nodeattrfuncDynamicTSCE(node):

    if node.is_leaf:
        return f'shape=box, color="#000000"'
    else:
        cSeqUUID = node.causalSequenceUUID
        if cSeqUUID is None:
            print(node.name + " has no causal sequence UUID", node.timestepCausalChild)
            return f'shape=box, color=red'
        hashed_uuid = uuid.uuid5(uuid.NAMESPACE_URL, cSeqUUID).hex
        r, g, b = int(hashed_uuid[:2], 16), int(hashed_uuid[2:4], 16), int(hashed_uuid[4:6], 16)
        color_code = "#{:02x}{:02x}{:02x}".format(r, g, b)
        return f'shape=box, color="{color_code}"'


# Causal Context, Sort By Variable Name Ansatz ####
def find_sequences(node:Node, verbose=False):

    cRoot = node.root 
    # 1. Starting of we consider each used causal context individually.
    cCausalContexts = list(set([cNode.causalContext for cNode in PreOrderIter(cRoot)]))
    cContextSequences = [] 
    changed = 0 
    for cCausalContext in cCausalContexts:
        cNodes = findall_by_attr(cRoot, cCausalContext, "causalContext")
        for node in cNodes:
            if all([cChild.causalContext == cCausalContext for cChild in node.children]):
                pass 
            else:
                node.transitionContext = node.children[0].causalContext 
                changed += 1
                
    for cCausalContext in cCausalContexts:

        cNodes = findall_by_attr(cRoot, cCausalContext, "causalContext")
        cNodesTransition = findall_by_attr(cRoot, cCausalContext, "transitionContext")
        cNodes = cNodes + cNodesTransition
        cVariables = list(set([cNode.name for cNode in cNodes]))

        cSequencesPerVariable = [] 
        for cVariable in cVariables:

            if verbose: print("Working with variable: " + cVariable + " in causal context: " + cCausalContext)

            cNodesByVariable = [cNode for cNode in cNodes if cNode.name == cVariable]
            cNodesByVariable = [cNode for cNode in cNodesByVariable if not cNode.is_leaf]
            cNodesByVariable.sort(key=lambda x: x.timestepCausalChild, reverse=True)

            cSequence = []
            cSequenceUUID = str(uuid.uuid4())
            cIndicators = {}
            for cNode in cNodesByVariable:

                if cIndicators == {}:
                    for cChild in cNode.children:
                        cIndicators["child_" + cChild.name] = cChild.indicator 
                    cSequence.append(cNode)
                    if verbose: print("Adding Start Node:", cNode.name, "Is root:", cNode.is_root)
                    
                else:
                    # Transition between Causal Contexts 
                    if cNode.children[0].causalContext != cCausalContext:
                        cIndicators = {}
                        if cSequence != []:
                            cSequencesPerVariable.append((cSequenceUUID, cSequence))
                            if verbose: print("Finishing Sequence.")
                        cSequence = []
                        cSequenceUUID = str(uuid.uuid4())
                        if verbose: print("Transition between causal contexts.", cNode.name, "Is root:", cNode.is_root)
                        break 

                    cMismatched = False 
                    for cChild in cNode.children:
                        if cIndicators["child_" + cChild.name] != cChild.indicator:
                            cMismatched = True 
                            break
                        else:
                            cSequence.append(cNode)
                            if verbose: print("Appending Node:", cNode.name, "Is root:", cNode.is_root)

                    if cMismatched:

                        if cSequence != []:
                            cSequencesPerVariable.append((cSequenceUUID, cSequence))
                            if verbose: print("Finishing Sequence.")

                        cIndicators = {}
                        cSequence = []
                        for cChild in cNode.children:
                            cIndicators["child_" + cChild.name] = cChild.indicator
                        cSequenceUUID = str(uuid.uuid4())
                        cSequence.append(cNode)
                        if verbose: print("Appending Node:", cNode.name, "Is root:", cNode.is_root)

            if cSequence != []: 
                cSequencesPerVariable.append((cSequenceUUID, cSequence))

        if cSequencesPerVariable != []:
            for cSeq in cSequencesPerVariable:
                cContextSequences.append(cSeq)

    for cUUID, seq in cContextSequences:
        for cNode in seq:
            cNode.causalSequenceUUID = cUUID

    return cContextSequences


def find_sequences2(node:Node, verbose=False):
    # Causal Context, Sort By Variable Name Ansatz ####
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

                cChildren = [i.split("_")[1] for i in cIndicators.keys() if "child_" in i]
                if set([cChild.name for cChild in cNode.children]) != set(cChildren):
                    print("Inside Transition.")
                    if cSequence != []:
                        cSequencesPerVariable.append((cSequenceUUID, cSequence))
                    cIndicators = {}
                    cSequence = []
                    for cChild in cNode.children:
                        cIndicators["child_" + cChild.name] = cChild.indicator
                    cSequenceUUID = str(uuid.uuid4())
                    cSequence.append(cNode)
                    continue

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
            cNode.causalSequenceUUID = cSequenceUUID

    return cSequencesPerVariable



def generateTreeImage(rootNode:Node, filepath):
    RenderTreeGraph(rootNode, nodenamefunc=nodenamefuncDynamicTSCE, nodeattrfunc=nodeattrfuncDynamicTSCE).to_picture(filepath)



        

































# Deprecated 
def doesSubTreeExist(nodeParent, newNode):
    # finding the root of the tree
    root = nodeParent.root 

    # finding the node in the tree
    nodes = [node for node in PreOrderIter(root)]
    for node in nodes:
        hasEquivalent = nodeEquivalent2Build(node, newNode)
        if hasEquivalent:
            return True

    return False  

# Function to find patterns in the tree. 

def getTreeDepth(node):
    return max([node.depth for node in PreOrderIter(node.root)])

def getAllChildsByDistance(root, distance):
    return [node for node in PreOrderIter(root) if root.depth == node.depth - distance]

def isChildOf(nodeParent, newNode):
    return newNode in list(nodeParent.children)

def sameChildNames(nodeParent, newNode):
    for child1, child2 in zip(nodeParent.children, newNode.children):
        if child1.name != child2.name:
            return False
    return True

def nodeEquivalentContinously(node1, node2):
    attrNames = ["indicator"]
    for attr in attrNames:
        if node1.__dict__[attr] != node2.__dict__[attr]:
            return False
    return True

def nodeEquivalent2Build(node1, node2):
    attrNames = list(node1.__dict__.keys())
    attrNames = [attrName for attrName in attrNames if "_" not in attrName]
    toRemove = ["uuid",  "parent"]

    for attr in toRemove:
        if attr in attrNames:
            attrNames.remove(attr)

    for attr in attrNames:
        if isinstance(node1.__dict__[attr], list):
            if len(node1.__dict__[attr]) != len(node2.__dict__[attr]):
                return False
            for i in range(len(node1.__dict__[attr])):
                if node1.__dict__[attr][i] != node2.__dict__[attr][i]:
                    return False
        elif attr == "children": # Only the case for children and indicator 
            for i in range(len(node1.children)):
                if not nodeEquivalent2Build(node1.children[i], node2.children[i]):
                    print("Comparing children")
                    return False
        else:
            if node1.__dict__[attr] != node2.__dict__[attr]:
                return False
    return True 

# Deprecated 
# All Paths Ansatz ####
def get_all_paths(node):
    cLeafs = [cLeaf for cLeaf in node.descendants if cLeaf.is_leaf]
    cPaths = [] 
    for cLeaf in cLeafs:
        cPaths.append(list(cLeaf.path))
    return cPaths


def find_longest_sequences(cRoot):

    cRoot = cRoot.root 
    cAllPaths = get_all_paths(cRoot)
    
    cAllSequences = [] 
    for cPath in cAllPaths:
        cSequencesPerPath = [] 
        cVariablesInPath = list(set([cNode.name for cNode in cPath]))
        cLenPath = len(cPath)

        for cVariable in cVariablesInPath:
            cStartIndexes = [i for i, x in enumerate([cNode.name for cNode in cPath]) if x == cVariable]
            cSequencePerVariable = []
            for cIndex in cStartIndexes:
                cSequencePerStartingIndex = []

                for cStep in range(1, cLenPath):
                    cSequence = [] 
                    cCurrParent = cPath[cIndex]
                    cCurrDistances = {}
                    cReachedEnd = False 
                    cCurrIndex = cIndex 
                    while not cReachedEnd:
                        

                        try:
                            cCurrIndex += cStep
                            cCurrChild = cPath[cCurrIndex]
                        except:
                            cReachedEnd = True 
                            continue

                        cCurrChild = cPath[cCurrIndex]
                        if cCurrChild.name == cVariable:
                            if sameChildNames(cCurrParent, cCurrChild): 
                                if cCurrDistances == {}:

                                    cComparisionFailed = False 
                                    for cChild1, cChild2 in zip(cCurrParent.children, cCurrChild.children):
                                        if nodeEquivalentContinously(cChild1, cChild2):
                                            cCurrDistances["child_" + cChild1.name] = cChild1.timestepParent - cChild2.timestepParent 
                                        else:
                                            cComparisionFailed = True
                                            break 

                                    if not cComparisionFailed:
                                        cCurrDistances["parent_" + cCurrParent.name] = cCurrParent.timestepParent - cCurrChild.timestepParent
                                        cSequence.append(cCurrParent)
                                        cSequence.append(cCurrChild) 
                                        cCurrParent = cCurrChild 
                                        continue 
                                    else:
                                        cReachedEnd = True 
                                        continue 
                                else:
                                    
                                    if cCurrParent.timestepParent != cCurrChild.timestepParent + cCurrDistances["parent_" + cCurrParent.name]:
                                        cReachedEnd = True 
                                        continue

                                    cComparisionFailed = False
                                    for cChild1, cChild2 in zip(cCurrParent.children, cCurrChild.children):
                                        if cChild1.timestepParent != cChild2.timestepParent + cCurrDistances["child_" + cChild1.name]:
                                            cComparisionFailed = True
                                            break
                                        if not nodeEquivalentContinously(cChild1, cChild2):
                                            cComparisionFailed = True
                                            break

                                    if not cComparisionFailed:
                                        cSequence.append(cCurrChild)
                                        cCurrParent = cCurrChild 
                                        continue 

                                    else:
                                        cReachedEnd = True 
                                        continue 
                            else:

                                if cCurrChild.is_leaf:
                                    print("Last node is leaf. Has same name but different children. (Edge case)")


                                cReachedEnd = True 
                                continue  
                        
                        else:
                            cReachedEnd = True 
                            continue

                    if cSequence != []:
                        cSequencePerStartingIndex.append(cSequence)

                if cSequencePerStartingIndex != []:
                    cSequencePerVariable.append(cSequencePerStartingIndex)

            if cSequencePerVariable != []:
                cSequencesPerPath.append(cSequencePerVariable)

        if cSequencesPerPath != []:
            cAllSequences.append(cSequencesPerPath)


    # Sammelsurium an Listen in Listen 
    cCleanedSequences = [i for sublist1 in cAllSequences for sublist2 in sublist1 for j in sublist2 for i in j]
    cLargestSequences = [] 
    # Reducing list to the longest sequences containing the same nodes 
    for cCleanedSequence in cCleanedSequences:

        if len(cCleanedSequence) < 3:
            continue 

        cCleanedSequenceSet = set(cCleanedSequence)
        cIsLargest = True 
        # compare to the rest 
        for cCompareSequence in cCleanedSequences:
            if cCleanedSequence != cCompareSequence:
                cCompareSequenceSet = set(cCompareSequence)
                if cCleanedSequenceSet.issubset(cCompareSequenceSet):
                    cIsLargest = False 
        if cIsLargest:
            cLargestSequences.append(cCleanedSequence)

    return cLargestSequences
