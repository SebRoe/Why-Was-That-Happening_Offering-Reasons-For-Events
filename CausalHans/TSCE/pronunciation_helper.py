def getPrefix():
    pass


def getInfix():
    pass


def getInfix(isSeq, num_relationTypes, idx_relationType, num_children, idx_child, node):
    if isSeq:
        return getInfixSeq(num_relationTypes, idx_relationType, num_children, idx_child, node)

    else:
        return getInfixClassic(num_relationTypes, idx_relationType, num_children, idx_child, node)



def getPrefixContinued(child, statusParent, rootIteration, pronomeUpper):

    tmp = f"{pronomeUpper} {statusParent}"+ " " + child.name + " "

    if child.iterationParent == rootIteration:
        tmp +=  "this year"

    else:
        timedifference = rootIteration - child.iterationParent
        timeVerbal = "years" if timedifference > 1 else "year"  
        tmp += f"{timedifference} {timeVerbal} ago"

    return tmp 





def getInfixClassic(num_relationTypes, idx_relationType, num_children, idx_child, node):

    tmp = "" 
    if idx_relationType == 0:
        if idx_child == 0:

            if not node.is_root:
                tmp += " is"

        elif idx_child == num_children - 1 and num_relationTypes - 1 == 0:
            tmp += " and"

        else:
            tmp += ","

    elif idx_relationType == num_relationTypes - 1:

        if idx_child == 0:
            tmp += " and"
        elif idx_child == num_children - 1:
            tmp += " and"
        else:
            tmp += "," 

    else:
        if idx_child == 0:
            tmp += ","
        elif idx_child == num_children - 1:
            tmp += ","
        else:
            tmp += ","  

    return tmp
def getTimeClassic(child, rootIteration):
    tmp = "" 
    if child.iterationParent == rootIteration:
        tmp += "this year"

    else:
        timedifference = rootIteration - child.iterationParent
        timeVerbal = "years" if timedifference > 1 else "year"  
        tmp += f"{timedifference} {timeVerbal} ago"

    return tmp 





def getInfixSeq(num_relationTypes, idx_relationType, num_children, idx_child, node):

    tmp = "" 
    if idx_relationType == 0:
        if idx_child == 0:
            lastElement = node.hasGetAttr("iterationParentLast")
            tmp += " constantly, over the last " + str(node.iterationParent - lastElement) + " years,"

            if not node.is_root:
                tmp += " is"

        elif idx_child == num_children - 1 and num_relationTypes - 1 == 0:
            tmp += " and"

        else:
            tmp += ","

    elif idx_relationType == num_relationTypes - 1:

        if idx_child == 0:
            tmp += " and"
        elif idx_child == num_children - 1:
            tmp += " and"
        else:
            tmp += "," 

    else:
        if idx_child == 0:
            tmp += ","
        elif idx_child == num_children - 1:
            tmp += ","
        else:
            tmp += ","  

    return tmp

def getTimeSeq(node, child):
    relativTimeToParent = node.iterationParent - child.iterationParent

    if relativTimeToParent == 0:
        timeToParent = "in the same year"
    elif relativTimeToParent == 1:
        timeToParent = "the year before"
    else:
        timeToParent = f"{relativTimeToParent} years before"

    return timeToParent