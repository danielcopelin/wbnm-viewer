import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


def plot_single_hydrograph(time, flow):

    fig, ax = plt.subplots()
    ax.plot(time, flow)
    fig.tight_layout()

    ax.set_xlabel("Time, minutes")
    ax.set_ylabel("Flow, cumecs")

    return fig


def box_plot(subarea, aep, peaks):

    selection = peaks.loc[
        (peaks.aep == aep) & (peaks.subarea == subarea) & (peaks.variable == "out")
    ]
    durations = selection.dur.unique()
    data = [
        list(selection.loc[selection.dur == duration, "value"])
        for duration in durations
    ]

    fig, ax = plt.subplots()
    ax.boxplot(data, labels=durations)

    ax.set_xlabel("Storm duration, minutes")
    ax.set_ylabel("Flow, cumecs")

    return fig

