import os
import re
import statistics
import csv

web_server_folders = ("actix-web-bench", "rocket-bench", "axum-bench")
server_type_folders = ("Normal", "Compression", "SingleThreaded")
workload_folders = ("Tiny", "Small", "Medium", "Large", "Dynamic")
concurrency_levels = ("1", "25", "50", "75", "100", "150", "200")

header = ("Web server", "Server type", "Workload type", "Concurrency level", "Failed reqs", "Requests per second",
          "Time per request (mean)", "Time per request (across concurrent reqs)", "Transfer rate")


def main():
    with open("results.csv", "w", newline="") as outcsv:
        writer = csv.writer(outcsv)
        writer.writerow(header)
        for web_server in web_server_folders:
            for server_type in server_type_folders:
                for workload_type in workload_folders:
                    for concurrency_level in concurrency_levels:
                        result_dir = os.path.join("Results", web_server, server_type, workload_type, concurrency_level)
                        print(f"Analyzing directory {result_dir}")
                        # Calculate the mean for each result in the three repetitions
                        fails = list()
                        rps_vals = list()
                        time_per_request_vals = list()
                        time_per_request_concurrent_vals = list()
                        transfer_rate_vals = list()
                        for i in (1, 2, 3):
                            with open(os.path.join(result_dir, f"{i}.txt")) as fp:
                                for line in fp.readlines():
                                    fail = re.findall(r"Failed requests: [ \t]*(\d+(?:\.\d+)?)", line)
                                    if len(fail) > 0:
                                        fails.append(float(fail[0]))
                                    rps = re.findall(r"Requests per second: [ \t]*(\d+(?:\.\d+)?)", line)
                                    if len(rps) > 0:
                                        rps_vals.append(float(rps[0]))
                                    tpr = re.findall(r"Time per request: [ \t]*(\d+(?:\.\d+)?) \[ms\] \(mean\)", line)
                                    if len(tpr) > 0:
                                        time_per_request_vals.append(float(tpr[0]))
                                    tprm = re.findall(r"Time per request: [ \t]*(\d+(?:\.\d+)?) \[ms\] \(mean, across all concurrent requests\)", line)
                                    if len(tprm) > 0:
                                        time_per_request_concurrent_vals.append(float(tprm[0]))
                                    tf = re.findall(r"Transfer rate: [ \t]*(\d+(?:\.\d+)?)", line)
                                    if len(tf) > 0:
                                        transfer_rate_vals.append(float(tf[0]))

                        fail = round(statistics.mean(fails), 3)
                        request_per_second = round(statistics.mean(rps_vals), 3)
                        time_per_request = round(statistics.mean(time_per_request_vals), 3)
                        time_per_request_concurrent = round(statistics.mean(time_per_request_concurrent_vals), 3)
                        transfer_rate = round(statistics.mean(transfer_rate_vals), 3)
                        writer.writerow((web_server, server_type, workload_type, concurrency_level, fail,
                                         request_per_second, time_per_request, time_per_request_concurrent,
                                         transfer_rate))


if __name__ == '__main__':
    main()
