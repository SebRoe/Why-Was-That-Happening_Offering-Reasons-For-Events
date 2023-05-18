from CausalHansTSCE import CausalHansInterpreterTSCE

def find_valid_id(data):
    for i in range(len(data.data)):
        try:
            id, patient_name = i, "Hans"
            data.select_entry(i, patient_name)

            interpreter = CausalHansInterpreterTSCE()
            Q_M = interpreter.Q(data, data.n2i["M"])
            pQ = interpreter.pronounce_Q(data, Q_M)
            print("The pronounciation of interest is: ", pQ)
            print("Found ID: ", id)
            return id
        except:
            pass

    print("No valid ID found")