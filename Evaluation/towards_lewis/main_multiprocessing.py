import multiprocessing as mp 
import queue, time, os
from multiprocessing import Process, Queue
import pandas as pd 
import tsce_datasethelper
import lewishelper # This is the helper file for the lewis counterfactuals
from sklearn.model_selection import train_test_split

import warnings
warnings.filterwarnings("ignore")





def processFunction(tasks_to_accomplish, tasks_that_are_done):
    while True:
        try:
            '''
                try to get task from the queue. get_nowait() function will 
                raise queue.Empty exception if the queue is empty. 
                queue(False) function would do the same task also.
            '''
        
            backdoors = {
                "Lagged_Age": [],
                "Lagged_Nutrition": ["Lagged_Age"],
                "Lagged_Health": ["Lagged_Age", "Lagged_Nutrition"],
                "Lagged_Mobility": ["Lagged_Health"],
                "Age": ["Lagged_Age"],
                "Nutrition": ["Lagged_Nutrition", "Age"],
                "Health": ["Lagged_Health"],
            }

            task = tasks_to_accomplish.get_nowait()
            print("Processing task: ", task[0], flush=True)
            
            counter, patient, columns, df = task 
            data = {'Feature': [], 'Nec Score': [], 'Suf Score': [], 'NeSuf Score': []}

            for feature in columns:
                all_other_keys = [i for i in patient.keys() if i != feature and i not in backdoors[feature]]
                all_other_values = [patient[i] for i in all_other_keys]
                patient_feature = patient[feature]
                alternative_feature = 1 if patient_feature == 0 else 0
                (n0, s0, sn0) = lewishelper.get_scores_regression(df, [feature],
                                                                  [patient_feature], # Swap this depending if you are interested in suf or nec score 
                                                                  [alternative_feature],
                                                                    all_other_keys,
                                                                    all_other_values,
                                                                    backdoors[feature],
                                                                    'Mobility')

                data['Feature'].append(feature)
                data['Nec Score'].append(n0)
                data['Suf Score'].append(s0)
                data['NeSuf Score'].append(sn0)

        except queue.Empty:
            print("Breaking - Queue empty.", flush=True)
            break

        except Exception as er:
            raise er

        else:
            '''
                if no exception has been raised, add the task completion 
                message to task_that_are_done queue
            '''
            tasks_that_are_done.put((data, patient))
            time.sleep(.5)


    return True
def wrapper_processes(patients, columns, df):
    number_of_processes =  mp.cpu_count() - 1  #min(number_of_task, mp.cpu_count() - 1)
    manager = mp.Manager()

    tasks_to_accomplish = Queue()
    tasks_that_are_done = manager.Queue()
    processes = []

    for counter, patient in enumerate(patients):
            tasks_to_accomplish.put((counter, patient, columns, df))

    # creating processes
    for w in range(number_of_processes):
        p = Process(target=processFunction, args=(tasks_to_accomplish, tasks_that_are_done)) 
        processes.append(p)
        p.start()
        time.sleep(.5)

    # completing process
    for p in processes:
        p.join()

    print("Processes joined.")
    results = [] 
    patientsUsed = [] 
    while not tasks_that_are_done.empty():
        rslt, patient = tasks_that_are_done.get()
        results.append(rslt)
        patientsUsed.append(patient)

    df = pd.concat([pd.DataFrame(i) for i in results])
    df.to_csv(f"results_below_{len(patients)}.csv") # Change String accordingly



if __name__ == "__main__":
    mp.freeze_support()

    data = pd.read_pickle("../data/counterfactual_tsce.pkl") # Change Path do data accordingly 
    df = data 
    y = df['Mobility']
    df.drop(['Mobility'], axis=1, inplace=True)
    X_train, X_test, y_train, y_test = train_test_split(df,
                                                        y, 
                                                        test_size=0.2, 
                                                        random_state=21)
    X_train["Mobility"] = y_train
    data = X_train
    (X_train, y_train, df, pred, model) = tsce_datasethelper.process_hans("randomforest", data)
    df["Mobility"] = pred

    yPred = model.predict(X_test)
    acc = [1 for i in range(len(y_test)) if y_test.values[i] == yPred[i]]
    print("Accuracy: ", len(acc)/len(yPred))

    columns = [i for i in df.columns if i != "Mobility"]

    # Selecting individuals with below average mobility
    ids = [i for i in range(len(X_test)) if yPred[i] == 0] # 0 is below average mobility, 1 is above average mobility
    # ids = ids[:50]
    patients = [dict(X_test.iloc[i]) for i in ids]
    patientsdf = pd.DataFrame(patients[:100])
    patientsdf.to_csv("patients_below_100.csv") # Change String accordingly

    wrapper_processes(patients[:100], columns, df)