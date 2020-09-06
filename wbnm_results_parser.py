# %%
from collections import defaultdict
import pandas as pd
import re
from dataclasses import dataclass


def get_peaks(meta_file):

    storm_columns = ["storm", "id", "aep", "dur", "ens", "type", "variable", "value"]
    peak_results_types = [
        "subarea",
        "out_str",
        "top",
        "bottom",
        "perv",
        "imp",
        "dir",
        "in",
        "out",
    ]
    peak_start_pattern = re.compile(
        r"""
        ^.+START_PEAK_SUMMARY.+:: # start of line
        (?=(.+-.+-.+-.+))               # storm
        (.+)-                           # id
        (.+)-                           # aep
        (.+)-                           # dur
        (.+)                            # ens
        \((.+)\)                        #type
        """,
        re.X,
    )
    peak_results_pattern = re.compile(
        r"""
        (\S+)\s+        # subarea
        (\d+\.?\d*)\s+  # out_str
        (\d+\.?\d*)\s+  # top
        (\d+\.?\d*)\s+  # bottom
        (\d+\.?\d*)\s+  # perb
        (\d+\.?\d*)\s+  # imp
        (\d+\.?\d*)\s+  # dir
        (\d+\.?\d*)\s+  # in
        (\d+\.?\d*)     # out
        """,
        re.X,
    )
    peak_end_pattern = re.compile(r"^.+END_PEAK_SUMMARY")

    peak_block = False
    with open(meta_file, "r") as infile:
        results = []
        for line in infile:
            peak_start_match = peak_start_pattern.findall(line)
            if peak_start_match:
                peak_block = True
                storm_dict = dict(zip(storm_columns, peak_start_match[0]))
                continue
            if peak_block:
                peak_end_match = peak_end_pattern.findall(line)
                if peak_end_match:
                    peak_block = False
                    continue
            if peak_block:
                peak_results_match = peak_results_pattern.findall(line)
                if peak_results_match:
                    peak_results_dict = dict(
                        zip(peak_results_types, peak_results_match[0])
                    )
                    storm_dict["subarea"] = peak_results_dict.pop("subarea")
                    for variable, value in peak_results_dict.items():
                        results.append(
                            {**storm_dict, "variable": variable, "value": float(value)}
                        )

    storms_df = pd.DataFrame(results)
    return storms_df


def get_hydrographs(meta_file, progress=None):

    hydrograph_columns = ["subarea", "storm", "id", "aep", "dur", "ens", "type"]
    results_columns = [
        "Time",
        "Rain",
        "Rainperv",
        "Qtop",
        "Qbot",
        "Qper",
        "Qimp",
        "Qinto_OS",
        "Qout_OS",
        "Stage",
    ]
    hydrograph_start_pattern = re.compile(
        r"""
        .+START_HYDROGRAPHS_    # start of line
        (\S+)\s*::              # sub area
        (?=(.+-.+-.+-.+))       # storm
        (.+)-                   # id
        (.+)-                   # aep
        (.+)-                   # dur
        (.+)                    # ens
        \((.+)\)                # type
        """,
        re.X,
    )
    hydrograph_results_pattern = re.compile(
        r"""
        (\d+\.?\d*)\s+  # Time
        (\d+\.?\d*)\s+  # Rain
        (\d+\.?\d*)\s+  # Rainperv
        (\d+\.?\d*)\s+  # Qtop
        (\d+\.?\d*)\s+  # Qbot
        (\d+\.?\d*)\s+  # Qper
        (\d+\.?\d*)\s+  # Qimp
        (\d+\.?\d*)\s+  # Qinto_OS
        (\d+\.?\d*)\s+  # Qout_OS
        (\d+\.?\d*)     # Stage
        """,
        re.X,
    )
    hydrograph_end_pattern = re.compile(r"#####END_HYDROGRAPHS_")

    hydrograph_no = 0

    hydrograph_block = False
    with open(meta_file, "r") as infile:
        hydrographs = defaultdict(dict)
        for line in infile:
            hydrograph_start_match = hydrograph_start_pattern.findall(line)
            if hydrograph_start_match:
                # update progress bar
                if progress:
                    progress.setValue(hydrograph_no)
                # initialise hydrograph
                hydrograph_block = True
                hydrograph_dict = dict(
                    zip(hydrograph_columns, hydrograph_start_match[0])
                )
                hydrograph = defaultdict(list)
                continue
            if hydrograph_block:
                hydrograph_end_match = hydrograph_end_pattern.findall(line)
                if hydrograph_end_match:
                    # process and compile hydrograph
                    hydrograph_block = False
                    hydrographs[hydrograph_dict["subarea"]][
                        hydrograph_dict["storm"]
                    ] = hydrograph
                    hydrograph_no += 1
                    continue
            if hydrograph_block:
                hydrograph_results_match = hydrograph_results_pattern.findall(line)
                if hydrograph_results_match:
                    # store line of hydrograph
                    for i, r in enumerate(results_columns):
                        hydrograph[r].append(float(hydrograph_results_match[0][i]))

    return hydrographs


if __name__ == "__main__":
    # %%
    storms_df = get_peaks(r"D:\03_Work\05_Code\wbnm\murarrie_Meta.out")
    storms_df.head()

    # %%
    hydrographs = get_hydrographs(r"D:\03_Work\05_Code\wbnm\murarrie_Meta.out")
    hydrographs.keys()

