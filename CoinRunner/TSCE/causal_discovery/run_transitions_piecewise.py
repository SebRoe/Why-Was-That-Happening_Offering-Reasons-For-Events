from helper import * 

def processFunction(tasks_to_accomplish, tasks_that_are_done):
    while True:
        try:
            '''
                try to get task from the queue. get_nowait() function will 
                raise queue.Empty exception if the queue is empty. 
                queue(False) function would do the same task also.
            '''
            task = tasks_to_accomplish.get_nowait()
            tmpDf, saving_path, saving_name, method, i = task 
            print(f"Process {current_process().name} doing task {i}", flush=True)

            G_pred = MAPMETHOD[method][0](tmpDf)
            df = pd.DataFrame(MAPMETHOD[method][1](G_pred), columns=tmpDf.columns, index=tmpDf.columns)
            if MAPMETHOD[method][2] is not None:
                df = MAPMETHOD[method][2](df)

            with open(os.path.join(saving_path, saving_name), "wb") as f:
                pickle.dump(df, f)

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
            tasks_that_are_done.put((df, f"Task {i} is done by " + mp.current_process().name))
            time.sleep(.5)


    return True
def wrapper_processes(processed_data: list, saving_names: list,  saving_path, method, plainDf):

    number_of_task = processed_data
    number_of_processes = min(len(number_of_task), mp.cpu_count())
    manager = mp.Manager()
    tasks_to_accomplish = Queue()
    tasks_that_are_done = manager.Queue()
    processes = []

    for counter, tmpDf in enumerate(number_of_task):
            tasks_to_accomplish.put((tmpDf, saving_path, saving_names[counter], method, counter))

    # creating processes
    for w in range(number_of_processes):
        p = Process(target=processFunction, args=(tasks_to_accomplish, tasks_that_are_done))
        processes.append(p)
        p.start()

    # completing process
    for p in processes:
        p.join()

    print("Processes joined.")

    # print the output
    processed_dfs = [] 
    while not tasks_that_are_done.empty():
        task, msg = tasks_that_are_done.get()
        processed_dfs.append(task)

    
RUN_METHODS = ["fci", "notearslin", "pc", "notears"]
#RUN_METHODS = ["notears"]
RUN_METHODS = ["fci", "pc"]
MAPMETHOD = {
    "fci": (run_fci, lambda x: x[0].graph, reduce_fci_time),
    "notearslin": (run_notearslin, lambda x: x, reduce_notears_time),
    "notears": (run_notears, lambda x: x["W"], reduce_notears_time),
    "pc": (run_pc, lambda x: x.G.graph, reduce_pc_time)
}

if __name__ == "__main__":
    mp.freeze_support()
    preprocessedDirNames, num_dirs = init2(DIRPATH, TAG, PREPROTAG, REDUCTIONTAG, equal_settings)
    print("Number of directories: ", num_dirs)

    for method in RUN_METHODS:
        for i in range(2,4):

            # Preparing data 
            processed_data = []
            saving_names = []  
            plainDfs = [] 
            data = read_recording_preprocessed(DIRPATH, preprocessedDirNames[i], PREPROTAG, REDUCTIONTAG)

            print("Rollout has length: ", len(data))

            for counter, frame in enumerate(data):
                if counter == 0:
                    continue 
                elif counter == len(data) - 1:
                    continue
                new_frame = {}
                first_frame = data[counter - 1]
                current_frame = data[counter]
                first_frame_updated = {f"{counter-1}_" + key: value for key, value in first_frame.items()}
                current_frame_updated = {f"{counter}_" + key: value for key, value in current_frame.items()}
                combined_frame = {**first_frame_updated, **current_frame_updated}
                tmpDf = pd.DataFrame([combined_frame])
                tmpDf = pd.concat([tmpDf]*100, ignore_index=True)
                tmpDf = tmpDf + np.random.normal(0, 0.1, tmpDf.shape)
                processed_data.append(tmpDf)
                saving_names.append(f"{method}_transition_piecewise_rollout_{i}_step_{counter - 1}_to_{counter}.pkl")


            plainDf = pd.DataFrame(columns=[f"{counter}_" + col for counter, frame in enumerate(data) for col in frame.keys()], index=[f"{counter}_" + col for counter, frame in enumerate(data) for col in frame.keys()])
            plainDf.fillna(0, inplace=True)

            saving_path = create_directory(os.path.join(f"{TAG}",  PREPROTAG.value, REDUCTIONTAG.value, f"{USE_ROLLOUT_UNTIL}", f"{method}", "transition_piecewise", f"rollout_{i}"))
            wrapper_processes(processed_data, saving_names, saving_path, method, plainDf)

    

