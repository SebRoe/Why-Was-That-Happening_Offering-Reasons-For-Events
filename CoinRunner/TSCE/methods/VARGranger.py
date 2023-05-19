from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.tsa.stattools import adfuller
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
from utils.graphs import create_timeseries_dag_gsi_1


class VARGranger():

    def __init__(self, df, indep_method="ssr_chi2test", significance_level=0.05):
        self.df = df 
        self.resultsDf = None
        self.threshold = None 
        self.indep_method = indep_method
        self.significance_level = significance_level


    def run(self, lag):
        self.lag = lag 

        self.model = VAR(self.df)
        self.results = self.model.fit(lag)

        self.variables = self.df.columns
        self.variablesTransformed = [f"{i}_{col}" for i in range(- lag, 1) for col in self.variables]

        self.num_variables = len(self.variables)
        self.num_variablesTransformed = len(self.variablesTransformed)

        self.resultsDf = pd.DataFrame(np.zeros((self.num_variablesTransformed, self.num_variablesTransformed)), index=self.variablesTransformed, columns=self.variablesTransformed)

        self.paramsDf = self.results.params
        self.pValuesDf = self.results.pvalues

        self.pValuesDfCleaned = self.pValuesDf.drop("const", axis=0, inplace=False)

        self.significances = [] 

        for i in self.pValuesDfCleaned.columns:
            tmp = {"effecting": i, "pot_causes": [], "confirmed_causes": []}
            for j in self.pValuesDfCleaned.index:
                if self.pValuesDfCleaned.loc[j,i] < self.significance_level:
                    lag = int(j.split(".")[0][1:])
                    varName = j.split(".")[1]
                    coef = round(self.paramsDf.loc[j,i], 3)
                    tmp["pot_causes"].append({"varName": varName, "lag": lag, "coef": coef})          
            self.significances.append(tmp)

        # Confirming significances with Granger Test. Dropping other potential causes
        for item in self.significances:
            effecting = item["effecting"]
            for potCause in item["pot_causes"]:
                varName, lag = potCause["varName"], potCause["lag"]
                pValue = self.specific_granger_test(data = self.df,  cause=varName, effect=effecting, lag=lag)
                if pValue < self.significance_level:
                    item["confirmed_causes"].append({"varName": varName, "lag": lag, "pValue": pValue, "coef": potCause["coef"]})

        for item in self.significances:
            effecting = item["effecting"] 
            for confirmedCause in item["confirmed_causes"]:
                varName, lag, coef = confirmedCause["varName"], confirmedCause["lag"], confirmedCause["coef"]
                self.resultsDf.loc[f"-{lag}_{varName}", f"{0}_{effecting}"] = coef

        self.resultsDf.fillna(0, inplace=True)


    def run2(self, lag):
        self.lag = lag 

        self.model = VAR(self.df)
        self.results = self.model.fit(lag)

        self.variables = self.df.columns
        self.variablesTransformed = [f"{i}_{col}" for i in range(- lag, 1) for col in self.variables]

        self.num_variables = len(self.variables)
        self.num_variablesTransformed = len(self.variablesTransformed)

        self.resultsDf = pd.DataFrame(np.zeros((self.num_variablesTransformed, self.num_variablesTransformed)), index=self.variablesTransformed, columns=self.variablesTransformed)

        self.paramsDf = self.results.params
        self.pValuesDf = self.results.pvalues

        self.pValuesDfCleaned = self.pValuesDf.drop("const", axis=0, inplace=False)

        self.significances = [] 

        for i in self.pValuesDfCleaned.columns:
            tmp = {"effecting": i, "pot_causes": [], "confirmed_causes": []}
            for j in self.pValuesDfCleaned.index:
                if self.pValuesDfCleaned.loc[j,i] < 0.05 or True:
                    lag = int(j.split(".")[0][1:])
                    varName = j.split(".")[1]
                    coef = round(self.paramsDf.loc[j,i], 3)
                    tmp["pot_causes"].append({"varName": varName, "lag": lag, "coef": coef})          
            self.significances.append(tmp)

        # Confirming significances with Granger Test. Dropping other potential causes
        for item in self.significances:
            effecting = item["effecting"]
            for potCause in item["pot_causes"]:
                varName, lag = potCause["varName"], potCause["lag"]

                results = self.results.test_causality(effecting, varName, kind="f", signif=self.significance_level)
                pValue = results.pvalue
                #pValue = self.specific_granger_test(data = self.df,  cause=varName, effect=effecting, lag=lag)
                
                if pValue < self.significance_level:
                    item["confirmed_causes"].append({"varName": varName, "lag": lag, "pValue": pValue, "coef": potCause["coef"]})

        for item in self.significances:
            effecting = item["effecting"] 
            for confirmedCause in item["confirmed_causes"]:
                varName, lag, coef = confirmedCause["varName"], confirmedCause["lag"], confirmedCause["coef"]
                self.resultsDf.loc[f"-{lag}_{varName}", f"{0}_{effecting}"] = coef

        self.resultsDf.fillna(0, inplace=True)


    def plotResults(self, threshold=0):
        tmpDf = self.resultsDf.copy()
        tmpDf[abs(tmpDf) < threshold] = 0
        create_timeseries_dag_gsi_1(tmpDf)
        

    def getResultsDf(self):
        return self.resultsDf


    def getDirectCauses(self, effect, threshold=0):
        df = self.resultsDf[f"0_{effect}"]
        df = df[df != 0]
        df = df.sort_values(ascending=False)
        df = df.to_frame()
        return df 

    def specific_granger_test(self, data, cause, effect, lag=1, verbose=False):

        test_result = grangercausalitytests(data[[effect, cause]], maxlag=[lag], verbose=False)
        p_values = [round(test_result[i][0][self.indep_method][1],4) for i in [lag]]
        if verbose: print(f'Y = {effect}, X = {cause}, P Values = {p_values}')
        min_p_value = np.min(p_values)
        return min_p_value


    def adfuller_wrapper(self, verbose=False):
        
        df = self.df.copy() 

        def adfuller_test(series, signif=0.05, name='', verbose=False):
            """Perform ADFuller to test for Stationarity of given series and print report"""
            r = adfuller(series, autolag='AIC')
            output = {'test_statistic':round(r[0], 4), 'pvalue':round(r[1], 4), 'n_lags':round(r[2], 4), 'n_obs':r[3]}
            p_value = output['pvalue'] 
            def adjust(val, length= 6): return str(val).ljust(length)

            # Print Summary

            

            if verbose:
                print(f'    Augmented Dickey-Fuller Test on "{name}"', "\n   ", '-'*47)
                print(f' Null Hypothesis: Data has unit root. Non-Stationary.')
                print(f' Significance Level    = {signif}')
                print(f' Test Statistic        = {output["test_statistic"]}')
                print(f' No. Lags Chosen       = {output["n_lags"]}')

            for key,val in r[4].items():
                if verbose: print(f' Critical value {adjust(key)} = {round(val, 3)}')

            if p_value <= signif:
                if verbose: print(f" => P-Value = {p_value}. Rejecting Null Hypothesis.")
                if verbose: print(f"{name} => Series is Stationary.")
                return (name, 1)
            else:
                if verbose: print(f" => P-Value = {p_value}. Weak evidence to reject the Null Hypothesis.")
                if verbose: print(f"{name} => Series is Non-Stationary.")
                return (name, 0)

        stationarities = [] 
        for name, column in df.items():
            stationarities.append(adfuller_test(column, name=column.name)) 

        for name, i in [(name, i) for name, i in stationarities if i == 1]:
            if verbose: print(f"{name} => Series is Stationary.")

        if verbose: print() 

        for name, i in [(name, i) for name, i in stationarities if i == 0]:
            if verbose: print(f"{name} => Series is not Stationary.")

        return [name for name, i in stationarities if i == 1]



    def plot_timeseries_raw(self):
        df = self.df 
        fig, axes = plt.subplots(nrows=len(df.columns)//2 + 1, ncols=2, dpi=120, figsize=(20,20))
        for i, ax in enumerate(axes.flatten()):
            try:
                data = df[df.columns[i]]
                ax.plot(data, color='red', linewidth=1)
                # Decorations
                ax.set_title(df.columns[i], fontsize=8)
                ax.xaxis.set_ticks_position('none')
                ax.yaxis.set_ticks_position('none')
                ax.spines["top"].set_alpha(0)
                ax.tick_params(labelsize=6)
                
            except:
                pass 

        # set the spacing between subplots
        plt.subplots_adjust(left=0.1,
                            bottom=0.1,
                            right=0.9,
                            top=0.9,
                            wspace=0.8,
                            hspace=0.4)
        plt.show()