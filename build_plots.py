import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter

header = ("Web server", "Server type", "Workload type", "Concurrency level", "Failed reqs", "Requests per second",
          "Time per request (mean)", "Time per request (across concurrent reqs)", "Transfer rate")

workload_types = ("Tiny", "Small", "Medium", "Large", "Dynamic")
server_types = ("Normal", "Compression", "SingleThreaded")

df = pd.read_csv('results.csv')
# Multiply by a factor of 1000 or 0.001 to have the columns in the proper format for the formatters used
df['Transfer rate'] = df['Transfer rate'].apply(lambda x: x * 1000)
df['Time per request (mean)'] = df['Time per request (mean)'].apply(lambda x: x * 0.001)
df['Time per request (across concurrent reqs)'] = df['Time per request (across concurrent reqs)'].apply(
    lambda x: x * 0.001)

columns = ['Requests per second', 'Time per request (mean)', 'Time per request (across concurrent reqs)',
           'Transfer rate']
column_formatters = [EngFormatter(unit='#/sec'), EngFormatter('s'), EngFormatter('s'),
                     EngFormatter('B/sec')]
column_higher_or_lower = ["higher is better", "lower is better", "lower is better", "higher is better"]


def main():
    for workload_type in workload_types:
        for server_type in server_types:
            tmp_df = df[(df['Server type'] == server_type) & (df['Workload type'] == workload_type)]
            # Each figure will have the plots for each result (4)
            fig, axes = plt.subplots(nrows=2, ncols=2, sharex='row')
            fig.suptitle(f"Workload: {workload_type}\nType: {server_type}")

            for i, column in enumerate(columns):
                dfp = tmp_df.pivot_table(index='Concurrency level', columns='Web server', values=column)
                plot = dfp.plot.bar(title=f"{column} ({column_higher_or_lower[i]})", legend=False,
                                    ax=axes[i % 2, i // 2])
                plot.yaxis.set_major_formatter(column_formatters[i])
                handles, labels = plot.get_legend_handles_labels()
                fig.legend(handles, labels, loc='lower center')

            plt.show()


if __name__ == '__main__':
    main()
