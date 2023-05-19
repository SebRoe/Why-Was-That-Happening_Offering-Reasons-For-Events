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

def wrapper_processes(processed_data: list, saving_names: list,  saving_path, method):

    number_of_task = processed_data
    number_of_processes = min(len(number_of_task), mp.cpu_count() - 1)
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
    while not tasks_that_are_done.empty():
        task, msg = tasks_that_are_done.get()

#RUN_METHODS = ["fci", "pc", "varlingam", "grangervar2", "lasso", "grangervar"]
RUN_METHODS = ["varlingam", "grangervar2", "lasso", "grangervar"]

MAPMETHOD = {
    "fci": (run_fci, lambda x: x[0].graph, reduce_fci_time),
    "pc": (run_pc, lambda x: x.G.graph, reduce_pc_time), 
}

if __name__ == "__main__":
    mp.freeze_support()
    preprocessedDirNames, num_dirs = init2(DIRPATH, TAG, PREPROTAG, REDUCTIONTAG, equal_settings)
    print("Number of directories: ", num_dirs)

    statesList = [
    {
        "enemyExists": False, 
        "powerupExists": False 
    },
    { 
        "enemyExists": True, 
        "powerupExists": False 
    },
    {
        "enemyExists": True, 
        "powerupExists": True 
    },
    ]


    for state in statesList:
        for method in RUN_METHODS:
            # Preparing data 
            processed_data = []
            saving_names = [] 
            if method != "lasso" and method != "grangervar" and method != "grangervar2" and method != "varlingam":
                for i in range(USE_ROLLOUT_UNTIL):
                    data = read_recording_preprocessed(DIRPATH, preprocessedDirNames[i], PREPROTAG, REDUCTIONTAG)

                    data = myFilter(data, margin=4, filter=state)
                    if data is None:
                        continue 
                    data = pd.concat([data]*10, ignore_index=True)

                    data = data + np.random.normal(0, 0.1, data.shape)
                    processed_data.append(data)
                    saving_names.append(f"{method}_summary_transition_1Step_rollout_{i}.pkl")

                saving_path = create_directory(os.path.join(f"{TAG}", PREPROTAG.value, REDUCTIONTAG.value, f"{USE_ROLLOUT_UNTIL}", f"{method}",  dictionary_to_string(state),"transition_1Step"))
                wrapper_processes(processed_data, saving_names, saving_path, method)

            else:
                for i in range(USE_ROLLOUT_UNTIL):
                    data = read_recording_preprocessed(DIRPATH, preprocessedDirNames[i], PREPROTAG, REDUCTIONTAG)
                    data = myFilter(data, margin=4, filter=state, transition=False)
                    if data is None:
                        continue 
                    data = pd.concat([data]*10, ignore_index=True)
                    df = data + np.random.normal(0, 0.1, data.shape)

                    saving_path = create_directory(os.path.join(f"{TAG}", PREPROTAG.value, REDUCTIONTAG.value, f"{USE_ROLLOUT_UNTIL}",  f"{method}", dictionary_to_string(state), "transition_1Step"))

                    if method == "lasso":
                        model = LassoGranger(df) 
                        model.run(lag=1, indep_test="ssr_ftest")

                    elif method == "grangervar":
                        model = VARGranger(df, indep_method="ssr_ftest")
                        model.run(lag=1) 

                    elif method == "grangervar2":
                        model = VARGranger(df, indep_method="ssr_ftest")
                        model.run2(lag=1)

                    elif method == "varlingam":
                        model = MyVARLiNGAM(df)
                        model.run(lag=1)

                    with open(os.path.join(saving_path, f"{method}_summary_transition_1Step_rollout_{i}_model.pkl"), "wb") as f:
                        #pickle.dump(model, f)
                        pass 
                    with open(os.path.join(saving_path, f"{method}_summary_transition_1Step_rollout_{i}.pkl"), "wb") as f:
                        pickle.dump(model.resultsDf, f)
                         

                dfs = []
                for i in range(0, USE_ROLLOUT_UNTIL):
                    data = read_recording_preprocessed(DIRPATH, preprocessedDirNames[i], PREPROTAG, REDUCTIONTAG)
                    df = myFilter(data, margin=4, filter=state, transition=False)
                    if df is None:
                        continue 
                    dfs.append(df)

                df = pd.concat(dfs, axis=0, ignore_index=True)
                display(df) 
                df = df + np.random.normal(0, 0.1, size=df.shape)

                saving_path = create_directory(os.path.join(f"{TAG}", PREPROTAG.value, REDUCTIONTAG.value, f"{USE_ROLLOUT_UNTIL}", f"{method}", dictionary_to_string(state), "transition_1Step"))
                if method == "lasso":
                    model = LassoGranger(df) 
                    model.run(lag=1, indep_test="ssr_ftest")

                elif method == "grangervar":
                    model = VARGranger(df, indep_method="ssr_ftest")
                    model.run(lag=1) 

                elif method == "grangervar2":
                    model = VARGranger(df, indep_method="ssr_ftest")
                    model.run2(lag=1)

                elif method == "varlingam":
                    model = MyVARLiNGAM(df)
                    model.run(lag=1)

                with open(os.path.join(saving_path, f"{method}_summary_transition_1Step_rollout_0_until_{USE_ROLLOUT_UNTIL}_model.pkl"), "wb") as f:
                    #pickle.dump(model, f)
                    pass 

                with open(os.path.join(saving_path, f"{method}_summary_transition_1Step_rollout_0_until_{USE_ROLLOUT_UNTIL}.pkl"), "wb") as f:
                    pickle.dump(model.resultsDf, f)
