import matplotlib.pyplot as plt


def load_metrics_from_file(filename):
    """Load metrics from a JSON file into an array."""
    with open(filename, 'r') as f:
        data = json.load(f)
    print(f"Metrics loaded from {filename}")
    return data

def plot_graphs_single(testname,options2,options1):
    file = "sysbench_" + testname + "_" + f"{(options1.replace('--', '').replace('=', '-'))}"
    for i in range(len(options2)):
        file = file + "_" + f"{(options2[i].replace('--', '').replace('=', '-'))}"
    file = file + ".json"
    file_no = "sysbench_results_no/" + file
    file_v1 = "sysbench_results_v1/" + file
    file_v2 = "sysbench_results_v2/" + file
    file_v2_1 = "sysbench_results_v2_1/" + file
    file_bhi = "sysbench_results_bhi/" + file
    
    metrics_no = load_metrics_from_file(file_no)
    metrics_v1 = load_metrics_from_file(file_v1)
    metrics_v2 = load_metrics_from_file(file_v2)
    metrics_v2_1 = load_metrics_from_file(file_v2_1)
    metrics_bhi = load_metrics_from_file(file_bhi)
    
    for i in metrics_no: 
        y = y.append(metrics_no[i]) 
        y = y.append(metrics_v1[i])
        y = y.append(metrics_v2[i])
        y = y.append(metrics_v2_1[i])
        y = y.append(metrics_bhi[i])
        
        x = ["none","v1","v2","v2_1","bhi"]
        
        plt.bar(x,y) 
        plt.xlabel('Spectre Mitigation')
        plt.ylabel(i)
        plt.title(i + " vs Spectre Mitigations")
    
    print(file_no)



threads = [1,10,100,1000]


plot_graphs_single("mutex",["--mutex-num=2048","--mutex-locks=10000"],"--threads=1")


