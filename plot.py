# This is based on https://github.com/matsui528/annbench/blob/main/plot.py
import argparse
import csv
import matplotlib
matplotlib.use('agg')
font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 20}

matplotlib.rc('font', **font)
import matplotlib.pyplot as plt
import sys
from itertools import cycle


styles = {'LMI': {'marker': 'p', 'linestyle': ':', 'color': 'red'},
          'HSP': {'marker': '^', 'linestyle': '-', 'color': 'blue'},
          'DEGLIB': {'marker': 'x', 'linestyle': '--', 'color': 'green'},
          'HIOB': {'marker': 'x', 'linestyle': ':', 'color': 'purple'},
          'BL-SearchGraph': {'marker': 'o', 'linestyle': '-', 'color': 'black'}
          }

def draw(lines, xlabel, ylabel, title, filename, with_ctrl, width, height):
    """
    Visualize search results and save them as an image
    Args:
        lines (list): search results. list of dict.
        xlabel (str): label of x-axis, usually "recall"
        ylabel (str): label of y-axis, usually "query per sec"
        title (str): title of the result_img
        filename (str): output file name of image
        with_ctrl (bool): show control parameters or not
        width (int): width of the figure
        height (int): height of the figure
    """
    plt.figure(figsize=(width, height))

    for line in lines:
        for key in ["xs", "ys", "label", "ctrls"]:
            assert key in line

    for line in lines:
        S = line["style"]
        plt.plot(line["xs"], line["ys"], label=line["label"], marker=S["marker"], linestyle=S["linestyle"], color=S["color"])
        if with_ctrl:
            for x, y, ctrl in zip(line["xs"], line["ys"], line["ctrls"]):
                plt.annotate(text=str(ctrl), xy=(x, y),
                             xytext=(x, y+50))

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(which="both")
    plt.yscale("log")
    plt.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left")
    #plt.legend(loc='best')
    plt.title(title)
    #plt.xticks(rotation=25)
    plt.subplots_adjust(bottom=0.15)
    plt.savefig(filename, bbox_inches='tight', dpi=300)
    plt.cla()

def get_pareto_frontier(line):
    data = sorted(zip(line["ys"], line["xs"], line["ctrls"]),reverse=True)
    line["xs"] = []
    line["ys"] = []
    line["ctrls"] = []

    cur = 0
    for y, x, label in data:
        if x > cur:
            cur = x
            line["xs"].append(x)
            line["ys"].append(y)
            line["ctrls"].append(label)

    return line

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csvfile")
    parser.add_argument("--title", default="")
    args = parser.parse_args()
    
    with open(args.csvfile, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        data = list(reader)
    
    lines = {}
    for res in data:
        algo = res["algo"]
        if algo.startswith("StochasticHIOB"):
            algo = "HIOB"
        elif algo.startswith("SearchGraph"):
            algo = "BL-SearchGraph"
        else:
            algo = algo.upper()

        label = algo
        if label not in lines:
            lines[label] =  {
                "xs": [],
                "ys": [],
                "ctrls": [],
                "label": label,
                "style": styles[label],
            }
        lines[label]["xs"].append(float(res["recall"]))
        lines[label]["ys"].append(10000/float(res["querytime"])) # FIX query size hardcoded
        run_identifier = res["params"] 
        lines[label]["ctrls"].append(run_identifier)
   
    outname = args.csvfile.replace(".csv", "") + ".png"
    with_ctrls = False
    draw([get_pareto_frontier(line) for line in lines.values()], 
            "Recall", "QPS (1/s)", args.title, outname, with_ctrls, 10, 8)
