from constants import *
from utils.enums import RecordingTag
from utils.graphs import create_timeseries_dag_gsi_1
from causallearn.search.FCMBased import lingam

class MyVARLiNGAM():

    def __init__(self, df):
        self.df = df 
        self.resultsDf = None
        self.threshold = None


    def run(self, lag):

        self.lag = lag 

        self.variables = self.df.columns
        self.variablesTransformed = [f"{i}_{col}" for i in range(- lag, 1) for col in self.variables]

        self.num_variables = len(self.variables)
        self.num_variablesTransformed = len(self.variablesTransformed)

        self.resultsDf = pd.DataFrame(np.zeros((self.num_variablesTransformed, self.num_variablesTransformed)), index=self.variablesTransformed, columns=self.variablesTransformed)

        self.model = lingam.VARLiNGAM(lags=lag, criterion=None, prune=False)
        self.model.fit(self.df.values) 
        self.coeffs = self.model.adjacency_matrices_ 

        dfs = [] 
        for i in range(0, self.lag + 1):
            curr_lag = i
            fromStr = f"-{curr_lag}_" if curr_lag != 0 else "0_"
            coeffs = self.coeffs[i]
            tmpDf = pd.DataFrame(coeffs, columns=[fromStr + i for i in self.df.columns], index=[f"0_" + i for i in self.df.columns])
            tmpDf = tmpDf.T 
            dfs.append(tmpDf)

        for df in dfs:
            for col in df.columns:
                for idx in df.index:
                    self.resultsDf.loc[idx, col] = df.loc[idx, col]

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

