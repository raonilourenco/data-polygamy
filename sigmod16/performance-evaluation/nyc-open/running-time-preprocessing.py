# Copyright (C) 2016 New York University
# This file is part of Data Polygamy which is released under the Revised BSD License
# See file LICENSE for full license details.

import os
import sys
import math
import matplotlib
matplotlib.use('Agg')
matplotlib.rc('font', family='sans-serif')
import matplotlib.pyplot as plt
import matplotlib.font_manager as font
import locale
locale.setlocale(locale.LC_ALL, 'en_US')

temp = {"hour": 4,
        "day": 3,
        "week": 2,
        "month": 1}

spatial = {"zip": 2,
           "city": 1}

if sys.argv[1] == "help":
    print "[metadata dir] [file] [use y label] [metadata file]"
    sys.exit(0)

phases = ["aggregates", "index", "relationship-restricted"]
legends = {"aggregates": "Scalar Function Computation",
           "index": "Feature Identification",
           "relationship-restricted": "Relationship Computation"}
phases_color = {"aggregates": "#003399",
                "index": "#0099CC",
                "relationship-restricted": "#66CCFF"}

metadata_dir = sys.argv[1]
use_y_label = eval(sys.argv[3])
metadata_file = sys.argv[4]

datasets = []
f = open(metadata_file)
line = f.readline()
while line != "":
    l = line.split(",")
    datasets.append(l[0])
    line = f.readline()

data = {"aggregates": {},
        "index": {},
        "relationship-restricted": {}}
f = open(sys.argv[2])
line = f.readline()
current_n_datasets = 0
max_n_datasets = -1
min_n_datasets = sys.maxint
while line != "":
    if line.endswith("datasets\n"):
        current_n_datasets = int(line.split(" ")[0])
        max_n_datasets = max(max_n_datasets, current_n_datasets)
        min_n_datasets = min(min_n_datasets, current_n_datasets)
    elif line.startswith("No "):
        pass
    elif line.strip() == "\n":
        pass
    elif line.startswith("Moved:"):
        pass
    else:
        l = line.split("\t")
        data[l[0]][current_n_datasets] = int(l[1])
    line = f.readline()

def get_number_combinations(data_dir, datasets, n):
    
    n_combinations = 0
    n_datasets = datasets[:n]

    # searching for files
    files = os.listdir(data_dir)
    for file in files:
        for dataset in n_datasets:
            data = dataset + "-"
            if data in file and not file.startswith("."):
                l = file.replace(".aggregates","").split("-")
                spatial_res = l[-1]
                temp_res = l[-2]

                f = open(os.path.join(data_dir,file))
                line = f.readline()
                n_combinations += (int(f.readline().strip())*temp[temp_res]*spatial[spatial_res])
                f.close()

    return n_combinations

def autolabel(rects_list, data):
    position_x = [0 for i in rects_list[0]]
    position_y = [0 for i in rects_list[0]]
    for rects in rects_list:
        index = 0
        for rect in rects:
            position_x[index] = rect.get_x()+rect.get_width()/2.
            position_y[index] += rect.get_height()
            index += 1
    # attach some text labels
    for i in range(len(data)):
        ax.text(position_x[i], position_y[i] + 0.5,
                locale.format('%d', int(data[i]), grouping=True), ha='center', va='bottom',
                fontproperties=font.FontProperties(style='italic',weight='bold'))

# plots
xlabel = "Number of Data Sets"
ylabel = "Time (min)"

plt.figure(figsize=(8, 6), dpi=80)

f, ax = plt.subplots()
ax.set_axis_bgcolor("#E0E0E0")

output = ""

datasets_to_show = [2]+range(30,301,30)
x_data = [(2*x)-0.5 for x in range(len(datasets_to_show))]

n_combinations = []
refs = []
bars = []
legend = []
previous = []
for i in datasets_to_show:
    previous.append(0)
    n_combinations.append(get_number_combinations(metadata_dir, datasets, i))
for phase in ["aggregates", "index"]:
    y_data = [float(data[phase][x])/60000 for x in datasets_to_show]
    bar = ax.bar(x_data, y_data, width=1.0, color=phases_color[phase], bottom=previous)
    output += phase + ": " + str(data[phase]) + "\n"
    refs.append(bar[0])
    bars.append(bar)
    legend.append(legends[phase])
    for i in range(len(previous)):
        previous[i] += y_data[i]

autolabel(bars, n_combinations)

plot_legend = ax.legend(refs, legend, handlelength=3, loc='upper left', borderpad=0.5, shadow=True, prop={'size':15,'style':'italic'})
plot_legend.get_frame().set_lw(0.5)

ax.set_xticks([2*x for x in range(len(datasets_to_show))])
ax.set_xticklabels([str(x) for x in datasets_to_show])

ax.tick_params(axis='y', labelsize=22)
ax.tick_params(axis='x', labelsize=16)

ax.spines["top"].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)

ax.set_xlim(-1,len(datasets_to_show)*2-1)
ax.set_ylim(ymax=225)
ax.set_xlabel(xlabel,fontproperties=font.FontProperties(size=22,weight='bold'))
if (use_y_label):
    ax.set_ylabel(ylabel,fontproperties=font.FontProperties(size=22,weight='bold'))

ax.grid(b=True, axis='both', color='w', linestyle='-', linewidth=0.7)
ax.set_axisbelow(True)

filename = "running-time-preprocessing"
plt.savefig(filename + ".png", bbox_inches='tight', pad_inches=0.05)
f = open(filename + ".out", "w")
f.write(output)
f.close()
plt.clf()
