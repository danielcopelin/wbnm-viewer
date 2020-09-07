from qgis.PyQt.QtWidgets import QVBoxLayout

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)


def update_plot(fig, widget, child=2):
    """[summary]

    Args:
        fig ([type]): [description]
        widget ([type]): [description]
        child (int, optional): [description]. Defaults to 2.
    """
    if len(widget.children()) > 0:
        canvas = widget.children()[child]
        old_ax = canvas.figure.get_axes()[0]
        new_ax = fig.get_axes()[0]

        # update lines
        for old_line, new_line in zip(old_ax.get_lines(), new_ax.get_lines()):
            old_line.set_xdata(new_line.get_xdata())
            old_line.set_ydata(new_line.get_ydata())

        # update legend if there is one
        old_legend, new_legend = old_ax.legend(), new_ax.legend()
        if old_legend:
            for old_text, new_text in zip(old_legend.texts, new_legend.texts):
                old_text._text = new_text._text

        old_ax.relim()
        old_ax.autoscale_view()
        canvas.draw_idle()
    else:
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, widget)
        layout = QVBoxLayout(widget)
        layout.addWidget(toolbar)
        layout.addWidget(canvas)


def single_hydrograph(time, flow):
    """[summary]

    Args:
        time ([type]): [description]
        flow ([type]): [description]

    Returns:
        [type]: [description]
    """
    fig, ax = plt.subplots()
    ax.plot(time, flow)
    fig.tight_layout()

    ax.set_xlabel("Time, minutes")
    ax.set_ylabel("Flow, cumecs")

    return fig


def box_plot(subarea, aep, peaks):
    """[summary]

    Args:
        subarea ([type]): [description]
        aep ([type]): [description]
        peaks ([type]): [description]

    Returns:
        [type]: [description]
    """
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


def ensembles(times, flows, storms):
    """[summary]

    Args:
        time ([type]): [description]
        flows ([type]): [description]
    """
    fig, ax = plt.subplots()
    for time, flow, storm in zip(times, flows, storms):
        ax.plot(time, flow, label=storm)
    fig.tight_layout()

    ax.set_xlabel("Time, minutes")
    ax.set_ylabel("Flow, cumecs")
    ax.legend()

    return fig
