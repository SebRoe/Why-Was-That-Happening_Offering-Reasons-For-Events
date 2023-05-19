#### Towards CoinRunner

This subfolder contains the CoinRunner game (coinrunner/), which can be executed through ./main.py. The game offers multiple configuration options (see coinrunner/constants.py). The ./main.py script also controls the recording functionality, allowing you to choose a tag under which relevant rollouts can be found. The program can also be run headless with custom deterministic agents. Agent behavior is controlled through ./main.py and coinrunner/Agent.py. It's worth mentioning that recorded rollouts are further processed later on. To provide enough flexibility, the current meta information is added to each rollout (./recordings).

The TSCE subfolder contains the Python files for reading, processing, learning causal time graphs, and generating causal explanations. Please note the TSCE/causal_discovery/settings.py file, which filters and selects recordings for learning the causal graphs. TSCE/causal_discovery/run_summary_transition_1Step.py generates a graph for each rollout based on the chosen methods and settings. These graphs need to be transferred from TSCE/causal_discovery/results to TSCE/DynTSCEGraphs manually. An example is already provided. Afterwards, explanations can be generated for new rollouts based on the learned graphs using TSCE/CoinRunnerExplainer.ipynb. For this purpose, the named rollouts under ./recordings/random/data in the repository are used. Depending on the game configuration, preprocessing needs to be performed as well. Therefore, the setting in CoinRunnerExplainer.ipynb is different from the one used for learning the agent behavior as 'Killer'.

##### Other Notes:

- TSCE\granger\MyGranger is an extended version of the code provided by the causal-learn Library. The original return values do not match the docstrings, so only one line was changed.

- Assets Licenses:

  - CC0: https://www.kenney.nl/assets/platformer-pack-redux
  - CC0: https://opengameart.org/content/background-2

  