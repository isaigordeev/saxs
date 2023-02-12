import random
from math import pi

# manage data and fit
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np



minq = -1
maxq = 1
N_peak = 100
trash_I = 1

dataExternal_example = [[1, 2], [2, 3], [3, 4]]
dataExternal = [[random.uniform(-minq - 1, +maxq + 1), random.uniform(-minq - 1, +maxq + 1)] for i in range(N_peak)]
# df = pd.read_csv("075773_treated_xye.csv", sep=';')
df = pd.read_csv("data/095221_xye.csv", sep=';')



# ax = df.plot(
#     x="Q", y="I",
#     kind="line", yerr="Di", title="peaks",
#     linestyle="", marker=".",
#     capthick=1, ecolor="gray", linewidth=1
# )
# plt.show()

def f_model(x, a, c):
    return pd.np.exp(( x-a)**2 / c)

df["model"] = f_model(df["Q"], 3, -2)
df.head()

# ax = df.plot(
#     x="Q", y="I",
#     kind="line", yerr="Di", title="Some experimetal data",
#     linestyle="", marker=".",
#     capthick=1, ecolor="gray", linewidth=1
# )
# ax = df.plot(
#     x="Q", y="model",
#     kind="line", ax=ax, linewidth=1
# )

plt.show()


class findPeaks(dataExternal):
    def construct(self):


        minq = -1
        maxq = 1
        N_peak = 100
        trash_I = 1


        knownPeaks = []
        phaseRules = []
        params = []
        searchWidePhasesQ = []

        # addPhases,check,data,widePeaksSave,
        # [IndentingNewLine]widePeaks,
        # IndentingNewLine]maxI,lpErr
        #
        # delWide,cubic,maxICubic,forCheckPairs,lonely

        def transform(peak):
            peak[1] = peak[1]/(2*pi)

        def gradient_descend(data):
            x = data[0]
            while(x-x)


        def data_filter(data):
            data_filtered = []
            for x in data:
                if x[1]>minq and x[1]< maxq and x[0] < trash_I:
                    data_filtered.append(x)

            return data_filtered

        print(data_filter(dataExternal))

        # empty peak
        # wide peak searching

        # without intensity\







