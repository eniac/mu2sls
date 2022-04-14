import matplotlib
import matplotlib.pyplot as plt

import numpy as np

class DataPoint:
    def __init__(self, rate, latencies = None, throughput = None, avg_latency = None):
        self.rate = rate
        if latencies is None:
            self.latencies = {}
        else:
            self.latencies = latencies
        self.throughput = throughput
        self.non2xx = 0
        self.requests = 0
        self.avg_latency = avg_latency

    def __repr__(self):
        return f'Point(r={self.rate},median_l={self.median_latency()},p90={self.ninety_latency()},t={self.throughput})'
    
    def set_latency(self, latency, percentile="50.000"):
        if latency.endswith("ms"):
            self.latencies[percentile] = round(float(latency.split("ms")[0]) * 1000)
        elif latency == "0.00us":
            self.latencies[percentile] = round(1000000000)
        elif latency.endswith("s"):
            self.latencies[percentile] = round(float(latency.split("s")[0]) * 1000000)
        else:
            assert False
    
    def set_throughput(self, throughput):
        self.throughput = float(throughput)

    def median_latency(self):
        return self.latencies["50.000"] if "50.000" in self.latencies else None
    
    def ninety_latency(self):
        return self.latencies["90.000"] if "90.000" in self.latencies else None
    
    def non2xx_out_of(self):
        return str(self.non2xx) + " out of: " + str(self.requests)


def parse_raw_wrk_results(log_file):
    with open(log_file) as f:
        lines = f.readlines()

    main_conf = None
    # print(data)
    curr_toggles = None
    curr_res = None
    results = {}
    for raw_line in lines:
        line = raw_line.rstrip().lstrip()


        if line.startswith("Running with:"):
            if curr_res is not None:
                # print(curr_res)
                curr_results.append(curr_res)
                curr_res = None
            
            if curr_toggles is not None:
                # print("Results:", curr_results)
                results[curr_toggles] = curr_results
                curr_results = []

            curr_toggles = line.split("Running with:")[1]
            curr_results = []            
            # print("Curr toggles:", curr_toggles)
        elif line.startswith("Executing:"):
            main_conf = line.split("Executing:")[1]
            # print("Main Conf:", main_conf)
        elif line.startswith("Rate:"):
            if curr_res is not None:
                # print(curr_res)
                curr_results.append(curr_res)
            rate = line.split("Rate: ")[1]
            curr_res = DataPoint(rate)
            # print("Rate:", rate)
        ## This is average latency, and therefore not useful
        elif line.startswith("Latency"):
            latency = line.split()[1]
            # curr_res.set_latency(latency)
            # print("Latency:", latency)
        elif line.startswith(("50.000%",
                              "75.000%",
                              "90.000%")):
            percentile = line.split("%")[0]
            latency = line.split()[1]
            curr_res.set_latency(latency, percentile)
        elif line.startswith("Non-2xx or 3xx responses:"):
            non2xx = line.split("Non-2xx or 3xx responses:")[1]
            curr_res.non2xx = int(non2xx)
        elif line.startswith("Requests/sec:"):
            throughput = line.split()[1]
            curr_res.set_throughput(throughput)
        elif "requests in" in line and "read" in line:
            requests = line.split()[0]
            curr_res.requests = int(requests)
        else:
            # print(line)
            pass
    
    if curr_toggles is not None:
        # print("Results:", curr_results)
        results[curr_toggles] = curr_results

    return results

label_map = {
    "": "no_log, no_txn",
    " --enable_logging": "log, no_txn",
    " --enable_txn": "no_log, txn",
    " --enable_logging --enable_txn": "log, txn",
    " --enable_txn --enable_custom_dict": "no log, txn, custom_dict",
    " --enable_logging --enable_txn --enable_custom_dict": "log, txn, custom_dict",
}

label_map = {
    # "": "μ2sls-base",
    "": "unsafe",
    # " --enable_logging": "μ2sls $-$OD $-$TX",
    # " --enable_logging": "TX-unsafe",
    " --enable_logging": "unsafe (w FT)",
    # " --enable_txn": "μ2sls $-$FT $-$OD",
    # " --enable_txn": "FT-unsafe",
    " --enable_txn": "no FT",
    # " --enable_logging --enable_txn": "μ2sls $-$OD",
    " --enable_logging --enable_txn": "μ2sls (w/o OD)",
    # " --enable_txn --enable_custom_dict": "μ2sls $-$FT",
    # " --enable_txn --enable_custom_dict": "FT-unsafe",
    " --enable_txn --enable_custom_dict": "no FT",
    " --enable_logging --enable_txn --enable_custom_dict": "μ2sls",
}

benchmark_map = {
    "single_stateful": "Stateful Counter",
    "chain": "Chain Counter",
    "tree": "Cross Service Txn",
    "media-service-test": "Media Application",
    "hotel-reservation": "Travel Reservation",
}

ylim_map = {
    "tree": 400,
    "media-service-test": 3000,
    "hotel-reservation": 1000,
}

plot_order = ["",
              " --enable_logging",
              " --enable_txn",
              " --enable_logging --enable_txn",
              " --enable_txn --enable_custom_dict",
              " --enable_logging --enable_txn --enable_custom_dict"]

single_threaded_results = {
    "single_stateful": {
            "": DataPoint(None, {"50.000":52.1}, throughput=19.08, avg_latency=52.4),
            " --enable_logging": DataPoint(None, {"50.000":52.0}, throughput=18.27, avg_latency=54.7),
        },
    "chain": {
            "": DataPoint(None, {"50.000":67.6}, throughput=16.60, avg_latency=60.2),
            " --enable_logging": DataPoint(None, {"50.000": 71.7}, throughput=15.92, avg_latency=62.8),
        },
    "tree": {
            "": DataPoint(None, {"50.000":65.1}, throughput=16.97, avg_latency=58.9),
            " --enable_logging": DataPoint(None, {"50.000":69.5}, throughput=15.51, avg_latency=64.4),
        },
    "media-service-test": {
            "": DataPoint(None, {"50.000":154.8}, throughput=6.9, avg_latency=144.8),
            " --enable_logging": DataPoint(None, {"50.000":152.1}, throughput=5.46, avg_latency=183.1),
        },
    "hotel-reservation": {
            "": DataPoint(None, {"50.000":57.8}, throughput=14.58, avg_latency=68.5),
            " --enable_logging": DataPoint(None, {"50.000":75.4}, throughput=14.28, avg_latency=69.9),
        },
}

label_colors = {}
cmap = matplotlib.cm.get_cmap('terrain')
color_linspace = np.linspace(0.0, 0.8, len(plot_order))[::-1]
for i in range(len(plot_order)):
    rgba = cmap(color_linspace[i])
    config_name = plot_order[i]
    label_colors[config_name] = rgba


def print_non2xx_res(res):
    # print("|-- non2xx")
    for dp in res:
        print_non_2xx_dp(dp)

def print_non_2xx_dp(dp):
    print("|---- WARNING: non-2xx:", dp.non2xx_out_of(), " -- for rate:", dp.rate)

## TODO: Label plots as tolerates faults, etc

## TODO: Buckets in custom Dict increase

## TODO: Get the mean and a big percentile instead of what we get now
def plot(plot_ax, results, benchmark, plot_order, debug=False):
    # print(benchmark)
    for key in plot_order:
    # for key, all_res in results.items():
        if key in results:
            # print("Plotting:", key)
            all_res = results[key]
            # print(key, res)
            ## We dont want the 1 rate result
            res = all_res[1:]
            xs = [dp.throughput for dp in res]
            ys = [dp.median_latency() / 1000.0 for dp in res]
            errors = [(0, dp.ninety_latency() / 1000.0 - dp.median_latency())
                    for dp in res]
            up_errors = [(dp.ninety_latency() - dp.median_latency()) / 1000.0
                        for dp in res]
            down_errors = [0 for dp in res]
            errors = (down_errors, up_errors)
            marker='.'
            plot_ax.errorbar(xs, ys, yerr=errors, label=label_map[key],
                        marker='.', 
                        color=label_colors[key],
                        capsize=3.0,
                        elinewidth=1,
                        linewidth=1.0,
                        zorder=1)
            ## Plot X markers if point is wrong
            if debug:
                for dp in res:
                    if dp.non2xx > 0:
                        print_non_2xx_dp(dp)
                        plot_ax.plot(dp.throughput,
                                    dp.median_latency() / 1000.0,
                                    marker='X',
                                    markersize=10.0,
                                    color='red',
                                    zorder=2)
                    if dp.requests == 0:
                        print("|---- WARNING: There were 0 completed requests for rate:", dp.rate)
    plot_ax.legend()
    plot_ax.set_ylabel('Latency (ms) (50th/90th)')
    plot_ax.set_xlabel('Throughput (requests/second)')
    ylim = 400
    if benchmark in ylim_map:
        ylim = ylim_map[benchmark]
    plot_ax.set_ylim(0, ylim)
    plot_ax.set_xlim(left=0)
    
def plot_fig(results, benchmark, plot_order, output_file_prefix="", debug=False):
    fig, ax = plt.subplots(1,1)
    plot(ax, results, benchmark, plot_order, debug=debug)
    fig.suptitle(benchmark_map[benchmark])
    filename = f"plots/{output_file_prefix}{benchmark}.pdf"
    fig.set_tight_layout(True)
    fig.set_size_inches(5, 4)
    plt.savefig(filename)


benchmarks = ["hotel-reservation"]

for benchmark in benchmarks:
    log_file = f"results/{benchmark}.log"
    results = parse_raw_wrk_results(log_file)
    from pprint import pprint
    plot_fig(results, benchmark, plot_order, debug=True)


##
## Logging benchmark
##
benchmarks = ["single_stateful",
              "chain"]

plot_order = ["",
              " --enable_logging"]

## Separate
for benchmark in benchmarks:
    log_file = f"results/{benchmark}.log"
    results = parse_raw_wrk_results(log_file)
    from pprint import pprint
    pprint(results)
    pprint("-" * 20)
    output_file_prefix = "logging_"
    plot_fig(results, benchmark, plot_order, output_file_prefix=output_file_prefix)

figsize=(9,2.5)
## TODO: Can we get these results instead?
plot_order = [" --enable_txn --enable_custom_dict",
              " --enable_logging --enable_txn --enable_custom_dict"]
# plot_order = ["",
#               " --enable_logging"]
##
## Combined
##
n = len(benchmarks)
fig, axs = plt.subplots(ncols=n, figsize=figsize,
                        # sharex=True, sharey=True,
                        constrained_layout=True)
for i in range(n):
    benchmark = benchmarks[i]
    log_file = f"results/{benchmark}.log"
    results = parse_raw_wrk_results(log_file)
    ax = axs[i]
    plot(ax, results, benchmark, plot_order[::-1])
    ax.set_xlabel(None)
    ax.set_title(benchmark_map[benchmark])
    if i > 0:
        ax.set(yticklabels=[])
        # ax.tick_params(left=False)
        ax.set(ylabel=None)
    if i < n-1:
        ax.get_legend().remove()

# fig.supylabel('Latency')
fig.supxlabel('Throughput (requests/second)')
fig.set_tight_layout(True)
filename = f"plots/logging_combined.pdf"
plt.savefig(filename)


##
## Transactions
##
benchmarks = ["single_stateful",
              "chain",
              "tree"]

plot_order = [" --enable_logging",
              " --enable_logging --enable_txn",
              " --enable_logging --enable_txn --enable_custom_dict"]

for benchmark in benchmarks:
    log_file = f"results/{benchmark}.log"
    results = parse_raw_wrk_results(log_file)
    output_file_prefix = "txn_"
    # print(results)
    plot_fig(results, benchmark, plot_order, output_file_prefix=output_file_prefix)

##
## Combined
##

n = len(benchmarks)
fig, axs = plt.subplots(ncols=n, figsize=figsize,
                        # sharex=True, sharey=True,
                        # constrained_layout=True
                        )
for i in range(n):
    benchmark = benchmarks[i]
    log_file = f"results/{benchmark}.log"
    results = parse_raw_wrk_results(log_file)
    from pprint import pprint
    ax = axs[i]

    plot(ax, results, benchmark, plot_order[::-1])

    ## Plot sequential
    st_res = single_threaded_results[benchmark]
    line = " --enable_logging"
    dp = st_res[line]  
    ax.axvline(x = dp.throughput, color = 'black', linestyle = '-.', label = 'unsafe-seq (w FT)')
    ax.legend()
    handles, labels = ax.get_legend_handles_labels()

    #specify order of items in legend
    order = [1,2,0,3]
    #add legend to plot
    ax.legend([handles[idx] for idx in order],[labels[idx] for idx in order])

    ax.set_xlabel(None)
    ax.set_title(benchmark_map[benchmark])
    if i > 0:
        ax.set(yticklabels=[])
        # ax.tick_params(left=False)
        ax.set(ylabel=None)
    if i > 0:
        ax.get_legend().remove()

# plt.subplots_adjust(wspace=0, hspace=0)

fig.supxlabel('Throughput (requests/second)')
fig.set_tight_layout(True)
plt.subplots_adjust(wspace=0)
filename = f"plots/txn_combined.pdf"
plt.savefig(filename)

##
## Real apps
##

benchmarks = ["media-service-test",
              "hotel-reservation"]

plot_order = ["",
              " --enable_logging --enable_txn --enable_custom_dict"]

for benchmark in benchmarks:
    log_file = f"results/{benchmark}.log"
    results = parse_raw_wrk_results(log_file)
    output_file_prefix = "real_apps_"
    # print(results)
    plot_fig(results, benchmark, plot_order, output_file_prefix=output_file_prefix)

n = len(benchmarks)
fig, axs = plt.subplots(ncols=n, figsize=figsize,
                        # sharex=True, sharey=True,
                        constrained_layout=True)
for i in range(n):
    benchmark = benchmarks[i]
    print(benchmark)
    log_file = f"results/{benchmark}.log"
    results = parse_raw_wrk_results(log_file)
    if benchmark == "media-service-test":
        a = DataPoint(80)
        a.latencies={"50.000": 1010000, "90.000": 2890000}
        a.throughput = 76.68
        results[""].append(a)
    pprint(results)
    ax = axs[i]
    plot(ax, results, benchmark, plot_order[::-1])

    ## Plot sequential
    st_res = single_threaded_results[benchmark]
    line = ""
    dp = st_res[line]  
    ax.axvline(x = dp.throughput, color = 'black', linestyle = '-.', label = 'unsafe-seq')
    ax.legend()
    handles, labels = ax.get_legend_handles_labels()

    #specify order of items in legend
    order = [1,0,2]
    #add legend to plot
    ax.legend([handles[idx] for idx in order],[labels[idx] for idx in order])

    ax.set_xlabel(None)
    ax.set_title(benchmark_map[benchmark])
    if i > 0:
        # ax.set(yticklabels=[])
        # ax.tick_params(left=False)
        ax.set(ylabel=None)
    if i < n-1:
        ax.get_legend().remove()

# fig.supylabel('Latency')
fig.supxlabel('Throughput (requests/second)')
fig.set_tight_layout(True)
filename = f"plots/apps_combined.pdf"
plt.savefig(filename)


## TODO: Make sure that we rerun experiments that look funky (maybe with 60s) and also make sure we reach limits of all apps.