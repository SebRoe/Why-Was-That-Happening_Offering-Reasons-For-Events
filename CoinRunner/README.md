#### Towards CoinRunner


Dieser Unterordner beinhaltet das Spiel CoinRunner (coinrunner/) ausführbar über die ./main.py. Das Spiel verfügt über mehrere Konfigurationsmöglichkeiten (siehe coinrunner/constants.py). Über die ./main.py lässt sich auch das Recording steuern, so kann man einen TAG auswählen, unter dessen Kategorie anschließend entsprechende Rollouts zu finden sind. Das Programm lässt sich auch Headless mit eigens definierten deterministischen Agenten laufen. Die Um-Implementation von RL Agenten sollte dementsprechend nicht kompliziert sein. Agentenverhalten wird über die ./main.py und coinrunner/Agent.py gesteuert. Erwähnenswert ist, dass aufgenommene Rollouts später weiter verarbeitet werden, um genug Spielraum zu haben werden dem Rollout die aktuellen Meta Informationen hinzugefügt. 

Im Unterordner TSCE befinden sich die Python Files zum auslesen, verarbeiten, anlernen der kausalen Zeitgraphen und generieren der kausalen Erklärungen. Zu beachten ist die TSCE/causal_discovery/settings.py, welche Recordings zum lernen der kausalen Graphen filtert und heraussucht. TSCE/causal_discovery/run_summary_transition_1Step.py generiert für jeden Rollout einen Graphen in abhängigkeit der gewählten Methoden und settings. Diese müssen anschließend nur vom TSCE/causal_discovery/results  in den TSCE/DynTSCEGraphs überführt werden. Ein Beispiel ist vorhanden. Anschließend kann mit TSCE/CoinRunnerExplainer.ipynb auf Basis der gelernten Graphen für neue Rollouts Erklärungen generiert werden. Hierzu dient im Repository die benannten Rollouts unter ./recordings/random/data. Hierfür muss je nach Spielkonfiguration ebenfalls ein Preprocessing durchgeführt werden, dass Setting in CoinRunnerExplainer.ipynb ist dementsprechend anders, als für das lernen des Agentenverhaltens `Killer'.



##### Other Notes:
- TSCE\granger\MyGranger is a extended version of the code provided from the causal-learn Library. The originals return value do not fit the docstrings. Just one line was changed. 
- Assets Licenses:
  - CC0: https://www.kenney.nl/assets/platformer-pack-redux
  - CC0: https://opengameart.org/content/background-2
- Please move the results directory to TSCE/