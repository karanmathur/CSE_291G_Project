import subprocess
import itertools
import os
import json 
import re 

def parse_sysbench_output(output):
    """Parse sysbench output to extract specific metrics."""
    metrics = {}

    # Extract avg latency
    latency_match = re.search(r"avg:\s+([\d.]+)", output)
    if latency_match:
        metrics["avg_latency"] = float(latency_match.group(1))

    # Extract value before cpu_core/cycles
    core_cycles_match = re.search(r"([\d,]+)\s+cpu_core/cycles:u/", output)
    if core_cycles_match:
        metrics["cpu_core_cycles"] = int(core_cycles_match.group(1).replace(",", ""))

    # Extract value before cpu_core/instructions/ and insn per cycle
    core_instructions_match = re.search(r"([\d,]+)\s+cpu_core/instructions:u/.*?#\s+([\d.]+)\s+insn per cycle", output)
    if core_instructions_match:
        metrics["cpu_core_instructions"] = int(core_instructions_match.group(1).replace(",", ""))
        metrics["insn_per_cycle"] = float(core_instructions_match.group(2))

    # Extract value before cpu_core/cache-misses/ and percentage
    cache_misses_match = re.search(r"([\d,]+)\s+cpu_core/cache-misses:u/.*?#\s+([\d.]+)% of all cache refs", output)
    if cache_misses_match:
        metrics["cpu_core_cache_misses"] = int(cache_misses_match.group(1).replace(",", ""))
        metrics["cache_miss_percentage"] = float(cache_misses_match.group(2))

    # Extract value before cpu_core/branch-misses/ and percentage
    branch_misses_match = re.search(r"([\d,]+)\s+cpu_core/branch-misses:u/.*?#\s+([\d.]+)% of all branches", output)
    if branch_misses_match:
        metrics["cpu_core_branch_misses"] = int(branch_misses_match.group(1).replace(",", ""))
        metrics["branch_miss_percentage"] = float(branch_misses_match.group(2))
    
    baclears_any_match = re.search(r"([\d,]+)\s+cpu_core/baclears\.any:u/", output)
    if baclears_any_match:
        metrics["cpu_core_baclears_any"] = int(baclears_any_match.group(1).replace(",", ""))

    # Extract value before cpu_core/br_inst_retired.all_branches:u/
    br_inst_retired_all_match = re.search(r"([\d,]+)\s+cpu_core/br_inst_retired\.all_branches:u/", output)
    if br_inst_retired_all_match:
        metrics["cpu_core_br_inst_retired_all_branches"] = int(br_inst_retired_all_match.group(1).replace(",", ""))

    # Extract value before cpu_core/br_misp_retired.all_branches:u/
    br_misp_retired_all_match = re.search(r"([\d,]+)\s+cpu_core/br_misp_retired\.all_branches:u/", output)
    if br_misp_retired_all_match:
        metrics["cpu_core_br_misp_retired_all_branches"] = int(br_misp_retired_all_match.group(1).replace(",", ""))

    # Extract value before cpu_core/br_inst_retired.cond:u/
    br_inst_retired_cond_match = re.search(r"([\d,]+)\s+cpu_core/br_inst_retired\.cond:u/", output)
    if br_inst_retired_cond_match:
        metrics["cpu_core_br_inst_retired_cond"] = int(br_inst_retired_cond_match.group(1).replace(",", ""))

    # Extract value before cpu_core/br_misp_retired.cond:u/
    br_misp_retired_cond_match = re.search(r"([\d,]+)\s+cpu_core/br_misp_retired\.cond:u/", output)
    if br_misp_retired_cond_match:
        metrics["cpu_core_br_misp_retired_cond"] = int(br_misp_retired_cond_match.group(1).replace(",", ""))

    # Extract value before cpu_core/br_inst_retired.indirect:u/
    br_inst_retired_indirect_match = re.search(r"([\d,]+)\s+cpu_core/br_inst_retired\.indirect:u/", output)
    if br_inst_retired_indirect_match:
        metrics["cpu_core_br_inst_retired_indirect"] = int(br_inst_retired_indirect_match.group(1).replace(",", ""))

    # Extract value before cpu_core/br_misp_retired.indirect_call:u/
    br_misp_retired_indirect_call_match = re.search(r"([\d,]+)\s+cpu_core/br_misp_retired\.indirect_call:u/", output)
    if br_misp_retired_indirect_call_match:
        metrics["cpu_core_br_misp_retired_indirect_call"] = int(br_misp_retired_indirect_call_match.group(1).replace(",", ""))

    return metrics

def save_metrics_to_file(metrics, filename):
    """Save metrics to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(metrics, f, indent=4)
    print(f"Metrics saved to {filename}")

def load_metrics_from_file(filename):
    """Load metrics from a JSON file into an array."""
    with open(filename, 'r') as f:
        data = json.load(f)
    print(f"Metrics loaded from {filename}")
    return data

def run_sysbench(testname, options1, options2, output_dir,perf_command):
    """Run sysbench with the specified options and save the output to a file."""
    # Build the sysbench command
    cmd =["sysbench"] + options2 + [testname] + options1 + ["run"]
    sysbench_fileio_prepare = ["sysbench","fileio","prepare"]
    #cmd = " ".join(cmd)
    perf_cmd = ["perf", "stat", "-e",
                "cycles,instructions,cache-references,cache-misses,branch-instructions,branch-misses,"
                "baclears.any,br_inst_retired.all_branches,br_misp_retired.all_branches,"
                "br_inst_retired.cond,br_misp_retired.cond,br_inst_retired.indirect,br_misp_retired.indirect_call"]
    full_cmd = perf_cmd + cmd
    #print(cmd)
    
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Build a filename for the output based on the options
    filename = os.path.join(
        output_dir,
        f"sysbench_{testname}_{'_'.join(o.replace('--', '').replace('=', '-') for o in options1 + options2)}.json"
    )
    print(filename)
    
    
    
    # Run the command and capture the output
    try:
        if(testname == "fileio"):
            subprocess.run(sysbench_fileio_prepare,check=True)
        result = subprocess.run(full_cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        print(result.stderr)
        metrics = parse_sysbench_output(result.stdout+result.stderr)
        save_metrics_to_file(metrics, filename)
        #with open(filename, "w") as f:
            #f.write(result.stdout)
        #print(f"Output saved to {filename}")
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(cmd)}: {e.stderr}")
        

# Define options and tests
def main():
    options1_combinations = list(itertools.product(
        ["--threads=1", "--threads=10","--threads=100","--threads=1000"],
        #["--thread-stack-size=32K", "--thread-stack-size=64K", "--thread-stack-size=128K"]
    ))

    tests = {
        "cpu": [],
        "fileio": [
            [f"--file-test-mode={mode}", f"--file-io-mode={io_mode}"]
            for mode in ["seqwr", "seqrewr", "seqrd", "rndrd", "rndwr", "rndrw"]
            for io_mode in ["sync", "async", "mmap"]
        ],
        "memory": [
            [
                f"--memory-block-size={block_size}",
                f"--memory-total-size={total_size}",
                #f"--memory-hugetlb={hugetlb}",
                #f"--memory-oper={oper}",
                #f"--memory-access-mode={access_mode}"
            ]
            for block_size in ["1K", "1M", "1G"]
            for total_size in ["1G", "10G", "100G"]
            #for hugetlb in ["on", "off"]
            #for oper in ["read", "write", "none"]
            #for access_mode in ["seq", "rnd"]
        ],
        "threads": [
            [
                f"--thread-yields={yields}",
                f"--thread-locks={locks}"
            ]
            for yields in [100, 1000, 10000]
            for locks in [4, 8, 16, 32]
        ],
        "mutex": [
            [
                f"--mutex-num={num}",
                f"--mutex-locks={locks}",
                #f"--mutex-loops={loops}"
            ]
            for num in [2048, 4096, 8192]
            for locks in [10000, 50000, 100000]
            #for loops in [5000, 10000, 20000]
        ]
    }

    output_dir = "sysbench_results_v1"
    perf_command = "perf stat -e cycles,instructions,cache-references,cache-misses,branch-instructions,branch-misses,baclears.any,br_inst_retired.all_branches,br_misp_retired.all_branches,br_inst_retired.cond,br_misp_retired.cond,br_inst_retired.indirect,br_misp_retired.indirect_call"
    i = 0 
    # Iterate over each test
    for testname, options2_list in tests.items():
        for options1 in options1_combinations:
            for options2 in options2_list or [[]]:
                options1_flat = list(options1)
                options2_flat = list(options2)
                run_sysbench(testname, options1_flat, options2_flat, output_dir,perf_command)
                i = i + 1
                print(i)
    print(i)

if __name__ == "__main__":
    main()
