import matplotlib.pyplot as plt

class DataPoint:
    def __init__(self, rate):
        self.rate = rate
        self.latencies = {}
        self.throughput = None

    def __repr__(self):
        return f'Point(r={self.rate},median_l={self.median_latency()},t={self.throughput})'
    
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
        return self.latencies["50.000"]
    
    def ninety_latency(self):
        return self.latencies["90.000"]


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
        elif line.startswith("Requests/sec:"):
            throughput = line.split()[1]
            curr_res.set_throughput(throughput)
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
    " --enable_logging --enable_txn": "log, txn"
}

benchmark_map = {
    "single_stateful": "Stateful Service",
    "chain": "3 Service Chain",
    "tree": "Cross Service Txn"
}

## TODO: Get the mean and a big percentile instead of what we get now
def plot(results, benchmark):
    fig = plt.figure()
    for key, all_res in results.items():
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
        plt.errorbar(xs, ys, yerr=errors, label=label_map[key],
                     marker='.', capsize=3.0,
                     elinewidth=1,
                     linewidth=1.0)
    plt.legend()
    plt.ylabel('Latency (ms) (50th/90th)')
    plt.xlabel('Throughput')
    plt.ylim(0, 400)
    plt.xlim(left=0)
    fig.suptitle(benchmark_map[benchmark])
    filename = f"plots/{benchmark}.pdf"
    plt.savefig(filename)

benchmarks = ["single_stateful",
              "chain",
              "tree"]

for benchmark in benchmarks:
    log_file = f"results/{benchmark}.log"
    results = parse_raw_wrk_results(log_file)
    # print(results)
    plot(results, benchmark)
