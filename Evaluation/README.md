To contextualize T-SCE with other methods, we had to rely on code from other authors. We cannot upload and share this code in our repository.



The authors of the Causal Shapley Values have made a public implementation of their code in R. Their code and an installation guide can be found here https://proceedings.neurips.cc/paper/2020/hash/32e54441e6382a7fbacbbbaf3c450059-Abstract.html. This is the supplement to "Causal Shapley Values: Exploiting Causal Knowledge to Explain Individual Predictions of Complex Models".

The R script "comparision_causal_hans_TSCE_classification" located in towards_causal_shapleys/ was used by us for data generation. Please be aware of any potential path errors. Our Causal Hans Classification dataset for import into the R script is located under data/. Our test results can be found under results/CausalShapleys. The script generates Sina Plots, as well as two CSV files for further processing and plotting.



The authors of the LEWIS method did not make their code publicly available, or we did not find it publicly. The authors were kind enough to provide us with a portion of their code. Our corresponding code is located under towards_lewis/. This involves two files. tsce_datahelper prepares the prediction model. main_multiprocessing.py generates all score predictions. The missing import can be found in the first lines here. There are also sections marked with comments to switch between Below Average and Above Average Mobility in order to generate traceable result files. The requirements.txt should contain all necessary packages. Here, too, we have compiled our results under results/LEWIS.



The subfolder plotting/ should be self-explanatory. The two Python notebooks use the results/* files and generate the SVG objects, which have been used in the main part.