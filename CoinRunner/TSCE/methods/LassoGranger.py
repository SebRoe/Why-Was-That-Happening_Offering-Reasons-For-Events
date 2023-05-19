from constants import *
from utils.enums import RecordingTag
from .MyGranger import Granger
from utils.graphs import create_timeseries_dag_gsi_1
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.tsa.stattools import adfuller


class LassoGranger():

    def __init__(self, df):
        self.df = df 
        self.resultsDf = None
        self.threshold = None


    def run(self, lag, indep_test="ssr_chi2test", significance_level=0.05):

        self.lag = lag 

        self.variables = self.df.columns
        self.variablesTransformed = [f"{i}_{col}" for i in range(- lag, 1) for col in self.variables]

        self.num_variables = len(self.variables)
        self.num_variablesTransformed = len(self.variablesTransformed)

        self.resultsDf = pd.DataFrame(np.zeros((self.num_variablesTransformed, self.num_variablesTransformed)), index=self.variablesTransformed, columns=self.variablesTransformed)

        self.granger = Granger(maxlag=lag, test=indep_test, significance_level=significance_level)
        self.coeffs = self.granger.granger_lasso(self.df.values)

        dfs = [] 
        for i in range(0, self.lag):
            curr_lag = i + 1
            coeffs = self.coeffs[i]
            tmpDf = pd.DataFrame(coeffs, columns=[f"-{curr_lag}_" + i for i in self.df.columns], index=[f"0_" + i for i in self.df.columns])
            tmpDf = tmpDf.T 
            dfs.append(tmpDf)

        for df in dfs:
            for col in df.columns:
                for idx in df.index:
                    self.resultsDf.loc[idx, col] = df.loc[idx, col]

        self.resultsDf.fillna(0, inplace=True)


    def run_2d(self, lag, indep_test="ssr_chi2test", significance_level=0.05):

        self.lag = lag 

        self.variables = self.df.columns
        self.variablesTransformed = [f"{i}_{col}" for i in range(- lag, 1) for col in self.variables]

        self.num_variables = len(self.variables)
        self.num_variablesTransformed = len(self.variablesTransformed)

        self.resultsDf = pd.DataFrame(np.zeros((self.num_variablesTransformed, self.num_variablesTransformed)), index=self.variablesTransformed, columns=self.variablesTransformed)
        
        self.granger = Granger(maxlag=lag, test=indep_test, significance_level=significance_level)

        for col1 in self.df.columns:
            for col2 in self.df.columns:
                if col1 != col2:
                    p_value_matrix, adj_matrix = self.granger.granger_test_2d(self.df[[col1, col2]].values)

        print(p_value_matrix.shape)
        print(p_value_matrix)
        print() 
        print(adj_matrix.shape)
        print(adj_matrix)

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

    def specific_granger_test(self, data, cause, effect, lag=1, indep_method="ssr_chi2test",verbose=False):

        test_result = grangercausalitytests(data[[effect, cause]], maxlag=[lag], verbose=False)
        p_values = [round(test_result[i][0][indep_method][1],4) for i in [lag]]

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

