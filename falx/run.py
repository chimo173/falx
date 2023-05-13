import argparse
import json
import logging

import pandas as pd
import os
import datetime
from pprint import pprint
import subprocess

from chart import VisDesign
from matplotlib_chart import MatplotlibChart
from eval_interface import FalxEvalInterface
import table_utils
from timeit import default_timer as timer

import morpheus

# default directories
PROJ_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DATA_DIR = os.path.join(PROJ_DIR, "examples")

# arguments
parser = argparse.ArgumentParser()
parser.add_argument("--data_dir", dest="data_dir", default=DATA_DIR, help="the directory of all benchmarks")
parser.add_argument("--data_id", dest="data_id", default= None,#"f03",
                    help="the id of the benchmark, if None, it runs for all tests in the data_dir")
parser.add_argument("--num_samples", dest="num_samples", default=16, type=int, help="the number of samples")
parser.add_argument("--backend", dest="backend", default="vegalite", type=str, help="visualization backend")
parser.add_argument("--prune", dest="prune", default="falx", type=str, help="prune strategy (falx, forward, morpheus)")

def test_benchmarks(data_dir, data_id, num_samples, backend, prune):
    """load the dataset into panda dataframes """
    test_targets = None
    # if data_id is not None:
    #     test_targets = [str(data_id) + '.json']
    # else:
    #     test_targets = [fname for fname in os.listdir(data_dir) if fname.endswith(".json")]

    if data_id is not None:
        test_targets = [str(data_id)]
    else:
        test_targets = [fname for fname in os.listdir(data_dir) if fname.endswith("in.json")]

    benchmarks = []
    task_res = 'falx-original.json'
    # task_res = 'falx-original.json'
    results = json.load(open(task_res, 'r'))

    import tqdm
    for fname in (test_targets):
        print(fname)
        fname = fname.split("_")[0]
        #print(fname)
        if not data_id and fname in results and results[fname]["prog"] != "[]":
            print(results[fname])
            print("skip")
            continue
        #exit()
        name_in = fname + "_in.json"
        name_out = fname + "_out.json"
        with open(os.path.join(data_dir, name_in), "r") as f:
            data_in = json.load(f)
        with open(os.path.join(data_dir, name_out), "r") as f:
            data_out = json.load(f)

        logging.info("input table:")
        pprint(data_in)
        #pprint(data_out)
        for row in data_out:
            for x in row:
                if isinstance(row[x], dict):
                    row[x] = row[x]["v"]

        logging.info("output table:")
        pprint(data_out)
        # with open(os.path.join(data_dir, fname), "r") as f:
        #     data = json.load(f)
        #
        # if not "vl_spec" in data:
        #     # ignore cases that do not have vl specs
        #     continue

        start = timer()
        print("====> run synthesize {}".format(fname))
        print("# num samples per layer: {}".format(num_samples))

        # read the dataset and create visualization
        #input_data = data["input_data"]
        #extra_consts = data["constants"] if "constants" in data else []
        #vis = VisDesign.load_from_vegalite(data["vl_spec"], data["output_data"])
        #trace = vis.eval()
        # pprint(trace)
        # exit()
        import concurrent.futures
        import  time
        try:
            #timeout = 1  # Timeout in seconds

            # with concurrent.futures.ThreadPoolExecutor() as executor:
            #     future = executor.submit(FalxEvalInterface.synthesize, inputs=[data_in], outputs=data_out, num_samples=num_samples,
            #                                   extra_consts=[], backend=backend, prune=prune)  # Specify the arguments by name
            #
            #     try:
            #         result = future.result(timeout)  # Wait for the result or timeout
            #         print(f"Result: {result}")
            #     except concurrent.futures.TimeoutError:
            #         result = "TLE"
            #         print("Function timed out")
            result = FalxEvalInterface.synthesize(inputs=[data_in], outputs=data_out, num_samples=num_samples,
                                              extra_consts=[], backend=backend, prune=prune)
        except:
            result = "RE"
        # result = FalxEvalInterface.synthesize(inputs=[input_data], full_trace=trace, num_samples=num_samples,
        #                                       extra_consts=extra_consts, backend=backend, prune=prune)
        end = timer()
        results[fname] = {}
        results[fname]["time"] = end - start
        results[fname]["prog"] = str(result)
        print(results[fname])

        json.dump(results, open(task_res, 'w'))
        # print("## synthesize result for task {}".format(fname))
        # for p, vis in result:
        #     print("# table_prog:")
        #     print("  {}".format(p))
        #     print("# vis_spec:")
        #     if backend == "vegalite":
        #         vl_obj = vis.to_vl_obj()
        #         data = vl_obj.pop("data")["values"]
        #         print("    {}".format(vl_obj))
        #     else:
        #         print(vis)
        #     print("# time used (s): {:.4f}".format(end - start))


if __name__ == '__main__':
    flags = parser.parse_args()
    test_benchmarks(flags.data_dir, flags.data_id, flags.num_samples, flags.backend, flags.prune)
