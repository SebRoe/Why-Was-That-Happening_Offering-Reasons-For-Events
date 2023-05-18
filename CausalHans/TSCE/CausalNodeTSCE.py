from anytree import Node, RenderTree, NodeMixin, Resolver, PostOrderIter, PreOrderIter
from anytree.exporter import DotExporter
from anytree.dotexport import RenderTreeGraph
import os, uuid 
from Utils.logger import get_spec_logger
from anytree.search import findall_by_attr

logger = get_spec_logger(__name__)


class CausalNodeTSCE(NodeMixin): 
    def __init__(self, name, person=None, causalParent=None, causalChild=None, timestepCausalParent=None, timestepCausalChild=None, muCausalParent=None, muCausalChild=None, valueCausalParent=None, valueCausalChild=None, parent=None, children=None, indicator=None, **kwargs):
        super().__init__()
        self.name = name
        self.person = person
        self.parent = parent
        self.indicator = indicator
        self.causalParent = causalParent
        self.causalChild = causalChild
        self.timestepCausalParent = timestepCausalParent
        self.timestepCausalChild = timestepCausalChild
        self.muCausalParent = muCausalParent
        self.muCausalChild = muCausalChild
        self.valueCausalParent = valueCausalParent
        self.valueCausalChild = valueCausalChild
        self.sequenceTag = None 
        self.__dict__.update(kwargs)
        self.uuid = uuid.uuid4()
        if children:
            self.children = children

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


    def containsSimilarSubTree(self, node:Node):
        include_attrs = ["timestepCausalParent"]
        cRoot = self.root 
        cSameNamedNodes = findall_by_attr(cRoot, node.name, "name")
        for cNode in cSameNamedNodes:
            if node == cNode:
                continue 
            attributes_same = True 
            for attr in include_attrs:
                if cNode.__dict__[attr] != node.__dict__[attr]:
                    attributes_same = False 
            if attributes_same:
                return True
        return False










"""
##### Functions to built the tree without doubled nodes

def getRootNode(anyNode:Node):
    is_root = False 
    while not is_root:
        if anyNode.is_root:
            is_root = True
        else:
            anyNode = anyNode.parent
    return anyNode

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


def doesSubTreeExist(nodeParent, newNode):
    # finding the root of the tree
    root = getRootNode(nodeParent)

    # finding the node in the tree
    nodes = [node for node in PreOrderIter(root)]
    for node in nodes:
        hasEquivalent = nodeEquivalent2Build(node, newNode)
        if hasEquivalent:
            return True

    return False  


############################################
##### Find Subtrees from different timesteps 
   
def findContinuedSameNamedSubTrees(root):

    FIRST_ITERATION = -1
    nodes = []
    for node in PreOrderIter(root):
        if len(node.children) == 0:
            continue 
        else:
            if node.iterationParent < FIRST_ITERATION or FIRST_ITERATION == -1:
                FIRST_ITERATION = node.iterationParent
            nodes.append(node)

    sequences = []
    nodes.sort(key=lambda x: x.iterationParent, reverse=True)


    for i in range(len(nodes)):
        currentParent = nodes[i]
        verbose = False 

        # Add check if its already markes or not. 
        reachedEnd = False
        distances = {}
        sequence = []
        while not reachedEnd:
            
            children = list(currentParent.children)

            if len(children) == 0:
                if verbose: print("No children")
                reachedEnd = True
                continue 
            
            if currentParent.name not in [node.name for node in children]:
                if verbose: print("No same name in children")
                reachedEnd = True
                continue
            else:
                child = children[[node.name for node in children].index(currentParent.name)]
                if sameChildNames(currentParent, child):
                    if distances == {}:
                        if verbose: print("Distance is not initialized")
                        for child1, child2 in zip(currentParent.children, child.children):
                            if not nodeEquivalentContinously(child1, child2):
                                distances = {}
                                reachedEnd = True
                                continue
                            distances[child1.name] = child1.iterationParent - child2.iterationParent

                        # if not nodeEquivalentContinously(currentParent, child):
                        #     distances = {}
                        #     reachedEnd = True
                        #     continue

                        distances[currentParent.name] = currentParent.iterationParent - child.iterationParent
                        sequence.append(currentParent)
                        sequence.append(child)
                        currentParent = child
                        continue

                    else:
                        for child1, child2 in zip(currentParent.children, child.children):
                            if child1.iterationParent != child2.iterationParent + distances[child1.name]:
                                if verbose: print("Distance Children is not the same")
                                reachedEnd = True
                                continue
                            
                            if not nodeEquivalentContinously(child1, child2):
                                reachedEnd = True
                                continue

                        if currentParent.iterationParent != child.iterationParent + distances[currentParent.name]:
                            if verbose: print("Distance Parent is not the same")
                            reachedEnd = True
                            continue 

                        if not nodeEquivalentContinously(currentParent, child):
                            reachedEnd = True
                            continue
                else:
                    if child.iterationChild != child.iterationParent:
                        if child.iterationParent != FIRST_ITERATION:
                            reachedEnd = True
                            continue

                sequence.append(child)
                currentParent = child
        
        if sequence != []:
            sequences.append(sequence)

    ## Adding meta informations to the top of the subtree containing a continously decreasing iteration number  
    largestCommonSequence = []
    for sequence in sequences:

        isLargest = True
        seqName = sequence[0].name 

        seqSet = set(sequence)

        for sequenceComp in [seq for seq in sequences if seq[0].name == seqName]:
            
            if sequence == sequenceComp:
                continue

            compSet = set(sequenceComp)
            if seqSet.issubset(compSet):
                isLargest = False
                break

        if isLargest:

            if len(sequence) <= 2:
                continue

            first = sequence[0]
            last = sequence[-1]

            distances = {}
            for child1, child2 in zip(first.children, sequence[1].children):
                distances[child1.name] = child1.iterationParent - child2.iterationParent
            distances[first.name] = first.iterationParent - sequence[1].iterationParent

            first.addAttr("isStartOfSequence", 1)
            first.addAttr("isEndOfSequence", 0)
            first.addAttr("sequenceDistances", distances)
            first.addAttr("iterationParentLast", last.iterationParent)

            for node in sequence[1:-1]:
                node.addAttr("isContinuedSequence", 1)


            last.addAttr("isEndOfSequence", 1)
            if [node.name for node in first.children] == [node.name for node in last.children]:
                last.addAttr("sameChildren", 1)
            else:
                last.addAttr("sameChildren", 0)

            largestCommonSequence.append(sequence)


    return largestCommonSequence


def getTreeDepth(node):
    root = getRootNode(node)
    return max([node.depth for node in PreOrderIter(root)])

def getAllChildsByDistance(root, distance):
    return [node for node in PreOrderIter(root) if root.depth == node.depth - distance]

def findSequences(root):

    FIRST_ITERATION = -1

    # Getting a list of all nodes in the tree in pre order
    nodes = []
    for node in PreOrderIter(root):
        if len(node.children) == 0:
            continue 
        else:
            if node.iterationParent < FIRST_ITERATION or FIRST_ITERATION == -1:
                FIRST_ITERATION = node.iterationParent
            nodes.append(node)

    # Sorting the nodes by iterationParent number. Sequence do start at a point higher than the following nodes. 
    
    nodes.sort(key=lambda x: x.iterationParent, reverse=True)


    # Step Counter we are interested in different sized steps of the time series. 
    sequences_by_depth = []
    for i in range(getTreeDepth(root)):
        sequences = [] 
        counter_steps = i + 1
        for i in range(len(nodes)):
            currentParent = nodes[i]
            verbose = False 

            # Add check if its already markes or not. 
            reachedEnd = False
            distances = {}
            sequence = []
            while not reachedEnd:
                childs_with_distance = [tmp_child for tmp_child in PreOrderIter(currentParent) if tmp_child.name == currentParent.name]
                parents_child_with_distance = getAllChildsByDistance(currentParent, counter_steps)
                childs_with_distance = [tmp_child for tmp_child in childs_with_distance if tmp_child in parents_child_with_distance]
                
                num_children_parent = len(currentParent.children)
                childs_with_distance = list(filter(lambda x: len(x.children) == num_children_parent, childs_with_distance))
                if len(childs_with_distance) == 0:
                    reachedEnd = True
                    continue
                elif len(childs_with_distance) > 1:
                    for i in childs_with_distance:
                        print(i.name, i.iterationParent)
                    print("CounterStep:", counter_steps)
                    print("CurrentParent:", currentParent.name, currentParent.iterationParent)
                    raise Exception("More than one child with distance")
                else:
                    child = childs_with_distance[0]

                if sameChildNames(currentParent, child):
                    if distances == {}:
                        if verbose: print("Distance is not initialized")
                        for child1, child2 in zip(currentParent.children, child.children):
                            if not nodeEquivalentContinously(child1, child2):
                                distances = {}
                                reachedEnd = True
                                continue
                            distances[child1.name] = child1.iterationParent - child2.iterationParent

    
                        distances[currentParent.name] = currentParent.iterationParent - child.iterationParent
                        sequence.append(currentParent)
                        sequence.append(child)
                        currentParent = child
                        continue

                    else:
                        for child1, child2 in zip(currentParent.children, child.children):
                            if child1.iterationParent != child2.iterationParent + distances[child1.name]:
                                if verbose: print("Distance Children is not the same")
                                reachedEnd = True
                                continue
                            
                            if not nodeEquivalentContinously(child1, child2):
                                reachedEnd = True
                                continue

                        if currentParent.iterationParent != child.iterationParent + distances[currentParent.name]:
                            if verbose: print("Distance Parent is not the same")
                            reachedEnd = True
                            continue 

                        if not nodeEquivalentContinously(currentParent, child):
                            reachedEnd = True
                            continue
                else:
                    if child.iterationChild != child.iterationParent:
                        if child.iterationParent != FIRST_ITERATION:
                            reachedEnd = True
                            continue

                sequence.append(child)
                currentParent = child
        
            if sequence != []:
                sequences.append((sequence, counter_steps))

        if sequences != []:
            sequences_by_depth.append(sequences)


    sequences_by_depth = [item for sublist in sequences_by_depth for item in sublist]
    ## Adding meta informations to the top of the subtree containing a continously decreasing iteration number  
    largestCommonSequence = []
    sequenceTag = 0 
    for sequence, counter_steps in sequences_by_depth:

        isLargest = True
        seqName = sequence[0].name 

        seqSet = set(sequence)

        for sequenceComp in [seq for seq, _ in sequences_by_depth if seq[0].name == seqName]:
            
            if sequence == sequenceComp:
                continue

            compSet = set(sequenceComp)
            if seqSet.issubset(compSet):
                isLargest = False
                break

        if isLargest:
            sequenceTag += 1
            if len(sequence) == 2:
                continue

            first = sequence[0]
            last = sequence[-1]

            distances = {}
            for child1, child2 in zip(first.children, sequence[1].children):
                distances[child1.name] = child1.iterationParent - child2.iterationParent
            distances[first.name] = first.iterationParent - sequence[1].iterationParent

            first.addAttr("isStartOfSequence", 1)
            first.addAttr("isEndOfSequence", 0)
            first.addAttr("sequenceDistances", distances)

            first.addAttr("stepsToChild", counter_steps)
            first.addAttr("sequenceTag", sequenceTag)
            for node in sequence[1:]:
                node.addAttr("isContinuedSequence", 1)
                node.addAttr("sequenceTag", sequenceTag)



            if len(last.children) == 0:
                last.addAttr("isEndOfSequence", 1)
                last.addAttr("sameChildren", 0)
            else:
                tmp = [child for child in last.children]
                if last.name in [i.name for i in tmp]:
                    last = [i for i in tmp if i.name == last.name][0]
                    last.addAttr("isEndOfSequence", 1)
                    last.addAttr("sameChildren", 1)
                    sequence.append(last)

            # if [node.name for node in first.children] == [node.name for node in last.children]:
            #     # if len(last.children) == 1 and counter_steps == 1:
            #     #     if len(last.children[0].children) == 0:
            #     #         print("Edge case")
            #     #         if nodeEquivalentContinously(last, last.children[0]):

            #     #             last.addAttr("isContinuedSequence", 1)
            #     #             last.addAttr("sequenceTag", sequenceTag)

            #     #             sequence.append(last.children[0])
            #     #             last = last.children[0]
            #     #             last.addAttr("isEndOfSequence", 1)
            #     #             last.addAttr("sequenceTag", sequenceTag)
            #     #             last.addAttr("sameChildren", 1)

            #     #             first.addAttr("iterationParentLast", last.iterationParent)

            #     #             continue
            #     #         else:
            #     #             print("Edge case failed")
            #     last.addAttr("sameChildren",1)
            # else:
            #     last.addAttr("sameChildren", 0)


            last.addAttr("isEndOfSequence", 1)
            last.addAttr("sequenceTag", sequenceTag)


                # Super Edge case for example Age

            

            first.addAttr("iterationParentLast", last.iterationParent)


            largestCommonSequence.append(sequence)

    print(len(largestCommonSequence))
    print(sequenceTag)
    return largestCommonSequence




def findSequencesV2(root):

    FIRST_ITERATION = -1

    # Getting a list of all nodes in the tree in pre order
    nodes = []
    for node in PreOrderIter(root):
        if len(node.children) == 0:
            continue 
        else:
            if node.iterationParent < FIRST_ITERATION or FIRST_ITERATION == -1:
                FIRST_ITERATION = node.iterationParent
            nodes.append(node)

    # Sorting the nodes by iterationParent number. Sequence do start at a point higher than the following nodes. 
    
    nodes.sort(key=lambda x: x.iterationParent, reverse=True)


    # Step Counter we are interested in different sized steps of the time series. 
    sequences_by_depth = []
    for i in range(getTreeDepth(root)):
        sequences = [] 
        counter_steps = i + 1
        for i in range(len(nodes)):
            currentParent = nodes[i]
            verbose = False 

            # Add check if its already markes or not. 
            reachedEnd = False
            distances = {}
            sequence = []
            while not reachedEnd:
                childs_with_distance = [tmp_child for tmp_child in PreOrderIter(currentParent) if tmp_child.name == currentParent.name]
                parents_child_with_distance = getAllChildsByDistance(currentParent, counter_steps)
                childs_with_distance = [tmp_child for tmp_child in childs_with_distance if tmp_child in parents_child_with_distance]
                
                num_children_parent = len(currentParent.children)
                childs_with_distance = list(filter(lambda x: len(x.children) == num_children_parent, childs_with_distance))
                if len(childs_with_distance) == 0:
                    reachedEnd = True
                    continue
                elif len(childs_with_distance) > 1:
                    for i in childs_with_distance:
                        print(i.name, i.iterationParent)
                    print("CounterStep:", counter_steps)
                    print("CurrentParent:", currentParent.name, currentParent.iterationParent)
                    raise Exception("More than one child with distance")
                else:
                    child = childs_with_distance[0]

                if sameChildNames(currentParent, child):
                    if distances == {}:
                        if verbose: print("Distance is not initialized")
                        for child1, child2 in zip(currentParent.children, child.children):
                            if not nodeEquivalentContinously(child1, child2):
                                distances = {}
                                reachedEnd = True
                                continue
                            distances[child1.name] = child1.iterationParent - child2.iterationParent

    
                        distances[currentParent.name] = currentParent.iterationParent - child.iterationParent
                        sequence.append(currentParent)
                        sequence.append(child)
                        currentParent = child
                        continue

                    else:
                        for child1, child2 in zip(currentParent.children, child.children):
                            if child1.iterationParent != child2.iterationParent + distances[child1.name]:
                                if verbose: print("Distance Children is not the same")
                                reachedEnd = True
                                continue
                            
                            if not nodeEquivalentContinously(child1, child2):
                                reachedEnd = True
                                continue

                        if currentParent.iterationParent != child.iterationParent + distances[currentParent.name]:
                            if verbose: print("Distance Parent is not the same")
                            reachedEnd = True
                            continue 

                        if not nodeEquivalentContinously(currentParent, child):
                            reachedEnd = True
                            continue
                else:
                    if child.iterationChild != child.iterationParent:
                        if child.iterationParent != FIRST_ITERATION:
                            reachedEnd = True
                            continue

                sequence.append(child)
                currentParent = child
        
            if sequence != []:
                sequences.append((sequence, counter_steps))

        if sequences != []:
            sequences_by_depth.append(sequences)


    sequences_by_depth = [item for sublist in sequences_by_depth for item in sublist]
    
    ## Adding meta informations to the top of the subtree containing a continously decreasing iteration number 
    for i in sequences_by_depth:
        if i[0][0].name == "Mobility":
            print([(i.name, i.iterationParent) for i in i[0]])

     
    largestCommonSequence = []
    sequenceTag = 0 
    for sequence, counter_steps in sequences_by_depth:

        isLargest = True
        seqName = sequence[0].name 

        seqSet = set(sequence)

        for sequenceComp in [seq for seq, _ in sequences_by_depth if seq[0].name == seqName]:
            
            if sequence == sequenceComp:
                continue

            compSet = set(sequenceComp)
            if compSet.issuperset(seqSet):
                isLargest = False
                break




        if isLargest:
            sequenceTag += 1
            if len(sequence) < 2:
                continue

            first = sequence[0]
            last = sequence[-1]

            distances = {}
            for child1, child2 in zip(first.children, sequence[1].children):
                distances[child1.name] = child1.iterationParent - child2.iterationParent
            distances[first.name] = first.iterationParent - sequence[1].iterationParent

            first.addAttr("isStartOfSequence", 1)
            first.addAttr("isEndOfSequence", 0)
            first.addAttr("sequenceDistances", distances)

            first.addAttr("stepsToChild", counter_steps)
            first.addAttr("sequenceTag", sequenceTag)
            for node in sequence[1:]:
                node.addAttr("isContinuedSequence", 1)
                node.addAttr("sequenceTag", sequenceTag)



            if len(last.children) == 0:
                last.addAttr("isEndOfSequence", 1)
                last.addAttr("sameChildren", 0)
            else:
                tmp = [child for child in last.children]
                if last.name in [i.name for i in tmp]:
                    last = [i for i in tmp if i.name == last.name][0]
                    last.addAttr("isEndOfSequence", 1)
                    last.addAttr("sameChildren", 1)
                    sequence.append(last)

            # TODO: Check if this is correct
            if [node.name for node in first.children] == [node.name for node in last.children]:
                if len(last.children) == 1 and counter_steps == 1:
                    if len(last.children[0].children) == 0:
                        print("Edge case")
                        if nodeEquivalentContinously(last, last.children[0]):

                            last.addAttr("isContinuedSequence", 1)
                            last.addAttr("sequenceTag", sequenceTag)

                            sequence.append(last.children[0])
                            last = last.children[0]
                            last.addAttr("isEndOfSequence", 1)
                            last.addAttr("sequenceTag", sequenceTag)
                            last.addAttr("sameChildren", 1)
                            

                            first.addAttr("iterationParentLast", last.iterationParent)

                            continue
                        else:
                            print("Edge case failed")
                last.addAttr("sameChildren",1)
            else:
                last.addAttr("sameChildren", 0)


            last.addAttr("isEndOfSequence", 1)
            last.addAttr("sequenceTag", sequenceTag)


                # Super Edge case for example Age

            

            first.addAttr("iterationParentLast", last.iterationParent)


            largestCommonSequence.append(sequence)

    for i in largestCommonSequence:
        print([(j.name, j.iterationParent) for j in i])

    return largestCommonSequence




def findSequencesV3(root):

    FIRST_ITERATION = -1

    # Getting a list of all nodes in the tree in pre order
    nodes = []
    for node in PreOrderIter(root):
        if len(node.children) == 0:
            continue 
        else:
            if node.iterationParent < FIRST_ITERATION or FIRST_ITERATION == -1:
                FIRST_ITERATION = node.iterationParent
            nodes.append(node)

    # Sorting the nodes by iterationParent number. Sequence do start at a point higher than the following nodes. 
    
    nodes.sort(key=lambda x: x.iterationParent, reverse=True)


    # Step Counter we are interested in different sized steps of the time series. 
    sequences_by_depth = []
    for i in range(getTreeDepth(root)):
        sequences = [] 
        counter_steps = i + 1
        for i in range(len(nodes)):

            currentParent = nodes[i]
            verbose = False  

            # Add check if its already markes or not. 
            reachedEnd = False
            distances = {}
            sequence = []
            while not reachedEnd:

                childs_with_distance = [tmp_child for tmp_child in PreOrderIter(currentParent) if tmp_child.name == currentParent.name]
                parents_child_with_distance = getAllChildsByDistance(currentParent, counter_steps)
                childs_with_distance = [tmp_child for tmp_child in childs_with_distance if tmp_child in parents_child_with_distance]
                
                num_children_parent = len(currentParent.children)
                childs_with_distance = list(filter(lambda x: len(x.children) == num_children_parent, childs_with_distance))

                
                if len(childs_with_distance) == 0:
                    reachedEnd = True
                    break
                elif len(childs_with_distance) > 1:
                    raise Exception("More than one child with distance found.")
                else: 
                    child = childs_with_distance[0]

            
                if sameChildNames(currentParent, child):
                    if verbose: print("They have same named children")

                    if distances == {}:
                        if verbose: print("Distances are not initialized yet.")
                        child_comparision_failed = False 
                        for child1, child2 in zip(currentParent.children, child.children):
                            if nodeEquivalentContinously(child1, child2):
                                distances["child_" + child1.name] = child1.iterationParent - child2.iterationParent
                            else:
                                child_comparision_failed = True 
                                break 

                        if not child_comparision_failed:
                            distances["parent_" + currentParent.name] = currentParent.iterationParent - child.iterationParent
                            sequence.append(currentParent)
                            sequence.append(child)
                            currentParent = child
                            if verbose: print(distances)
                            continue 
                        else:
                            distances = {}
                            reachedEnd = True 
                            continue 

                    else:

                        if currentParent.iterationParent != child.iterationParent + distances["parent_" + currentParent.name]:
                            if verbose: print("Parent iteration parent is not correct")
                            distances = {}
                            reachedEnd = True 
                            continue  

                        child_comparision_failed = False
                        for child1, child2 in zip(currentParent.children, child.children):

                            if child1.iterationParent != child2.iterationParent + distances["child_" + child1.name]:
                                if verbose: print("Distance Children are not the same")
                                child_comparision_failed = True
                                break 
                            if not nodeEquivalentContinously(child1, child2):
                                child_comparision_failed = True
                                break 

                        if not child_comparision_failed:
                            sequence.append(child)
                            currentParent = child
                            continue
                        else:
                            reachedEnd = True 
                            continue

                else:
                    if verbose: print("They have different named children")
                    reachedEnd = True 
                    continue  

            if sequence != []:
                sequences.append((sequence, counter_steps))

        if sequences != []:
            sequences_by_depth.append(sequences)


    sequences_by_depth = [item for sublist in sequences_by_depth for item in sublist]
    
    ## Adding meta informations to the top of the subtree containing a continously decreasing iteration number 
    # for i in sequences_by_depth:
    #     if i[0][0].name == "Mobility":
    #         print([(i.name, i.iterationParent) for i in i[0]])

     
    largestCommonSequence = []
    sequenceTag = 0 
    for sequence, counter_steps in sequences_by_depth:

        isLargest = True
        seqName = sequence[0].name 

        seqSet = set(sequence)

        for sequenceComp in [seq for seq, _ in sequences_by_depth if seq[0].name == seqName]:
            
            if sequence == sequenceComp:
                continue

            compSet = set(sequenceComp)
            if compSet.issuperset(seqSet):
                isLargest = False
                break




        if isLargest:
            sequenceTag += 1
            if len(sequence) < 2:
                continue

            first = sequence[0]
            last = sequence[-1]

            distances = {}
            for child1, child2 in zip(first.children, sequence[1].children):
                distances[child1.name] = child1.iterationParent - child2.iterationParent
            distances[first.name] = first.iterationParent - sequence[1].iterationParent

            first.addAttr("isStartOfSequence", 1)
            #first.addAttr("isEndOfSequence", 0)
            first.addAttr("sequenceDistances", distances)

            first.addAttr("stepsToChild", counter_steps)
            first.addAttr("sequenceTag", sequenceTag)
            for node in sequence[1:]:
                node.addAttr("isContinuedSequence", 1)
                node.addAttr("sequenceTag", sequenceTag)



            if len(last.children) == 0:
                last.addAttr("isEndOfSequence", 1)
                last.addAttr("sameChildren", 0)
            else:
                tmp = [child for child in last.children]
                if last.name in [i.name for i in tmp]:
                    last = [i for i in tmp if i.name == last.name][0]
                    last.addAttr("isEndOfSequence", 1)
                    last.addAttr("sameChildren", 1)
                    sequence.append(last)

            # TODO: Check if this is correct
            if [node.name for node in first.children] == [node.name for node in last.children]:
                if len(last.children) == 1 and counter_steps == 1:
                    if len(last.children[0].children) == 0:
                        print("Edge case")
                        if nodeEquivalentContinously(last, last.children[0]):

                            last.addAttr("isContinuedSequence", 1)
                            last.addAttr("sequenceTag", sequenceTag)

                            sequence.append(last.children[0])
                            last = last.children[0]
                            last.addAttr("isEndOfSequence", 1)
                            last.addAttr("sequenceTag", sequenceTag)
                            last.addAttr("sameChildren", 1)
                            

                            first.addAttr("iterationParentLast", last.iterationParent)

                            continue
                        else:
                            print("Edge case failed")
                last.addAttr("sameChildren",1)
            else:
                last.addAttr("sameChildren", 0)


            last.addAttr("isEndOfSequence", 1)
            last.addAttr("sequenceTag", sequenceTag)


                # Super Edge case for example Age

            

            first.addAttr("iterationParentLast", last.iterationParent)


            largestCommonSequence.append(sequence)

    # for i in largestCommonSequence:
    #     print([(j.name, j.iterationParent) for j in i])

    return largestCommonSequence




"""


