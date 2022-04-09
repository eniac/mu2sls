import matplotlib.pyplot as plt

class DataPoint:
    def __init__(self, rate):
        self.rate = rate
        self.latency = None
        self.throughput = None

    def __repr__(self):
        return f'Point(r={self.rate},l={self.latency},t={self.throughput})'
    
    def set_latency(self, latency):
        if latency.endswith("ms"):
            self.latency = round(float(latency.split("ms")[0]) * 1000)
        elif latency.endswith("s"):
            self.latency = round(float(latency.split("s")[0]) * 1000000)
        else:
            assert False
    
    def set_throughput(self, throughput):
        self.throughput = float(throughput)



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
            if curr_toggles is not None:
                # print("Results:", curr_results)
                results[curr_toggles] = curr_results

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
        elif line.startswith("Latency"):
            latency = line.split()[1]
            curr_res.set_latency(latency)
            # print("Latency:", latency)
        elif line.startswith("Requests/sec:"):
            throughput = line.split()[1]
            curr_res.set_throughput(throughput)
        else:
            pass
            # print(line)
    
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
    "single_stateful": "Stateful Service"
}

## TODO: Get the mean and a big percentile instead of what we get now
def plot(results, benchmark):
    fig = plt.figure()
    for key, all_res in results.items():
        # print(key, res)
        ## We dont want the 1 rate result
        res = all_res[1:]
        xs = [dp.throughput for dp in res]
        ys = [dp.latency / 1000.0 for dp in res]
        plt.plot(xs, ys, label=label_map[key],
                 marker='.')
    plt.legend()
    plt.ylabel('Latency (ms)')
    plt.xlabel('Throughput')
    plt.ylim(0, 400)
    fig.suptitle(benchmark_map[benchmark])
    filename = f"plots/{benchmark}.pdf"
    plt.savefig(filename)

log_file = "results/single_stateful.log"
results = parse_raw_wrk_results(log_file)
plot(results, "single_stateful")