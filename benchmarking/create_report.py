import json
from csv import DictWriter
from pathlib import Path

from benchmarking.auditing import get_auditing_results_path
from benchmarking.benchmarking_utils import get_benchmark_results_dir, iter_all_benchmarks
from benchmarking.timing import get_timing_results_path
from benchmarking.analyze_profile_results import get_top_n_cumtime_funcs

# TODO: instead of a single report, remove the benchmarking results (top_n) from the report,
#   and, for each benchmark, create a table with the function and how much time it took
#   and another table for all the benchmarks together


def get_report_dir() -> Path:
    report_dir = get_benchmark_results_dir() / 'reports'
    report_dir.mkdir(exist_ok=True)
    return report_dir


def create_report():
    """The report is organized as follows:
        - it is in .csv format for easy reading
    :return: None
    """
    top_n = 20
    lines = []
    report_dir = get_report_dir()

    for benchmark in iter_all_benchmarks():
        line = {'name': benchmark.name, 'query': benchmark.query}

        timing_results_path = get_timing_results_path(benchmark)
        with timing_results_path.open('r') as f:
            timing_results = json.load(f)
            line.update(timing_results)

        auditing_results_path = get_auditing_results_path(benchmark)
        with auditing_results_path.open('r') as f:
            auditing_results = json.load(f)
            line.update(auditing_results)

        lines.append(line)

        # TODO: refactor this into a function
        top_func_records = get_top_n_cumtime_funcs(top_n, benchmark)
        top_func_report_path = report_dir / f'{str(benchmark)}_top_func_report.csv'
        with top_func_report_path.open('w', newline='') as f:
            writer = DictWriter(f, fieldnames=top_func_records[0].keys())
            writer.writeheader()
            writer.writerows(top_func_records)

    top_func_records = get_top_n_cumtime_funcs(top_n)
    top_func_report_path = report_dir / f'accumulated_top_func_report.csv'
    with top_func_report_path.open('w', newline='') as f:
        writer = DictWriter(f, fieldnames=top_func_records[0].keys())
        writer.writeheader()
        writer.writerows(top_func_records)

    timing_report_path = report_dir / 'timing_report.csv'
    with timing_report_path.open('w', newline='') as f:
        writer = DictWriter(f, fieldnames=lines[0].keys())
        writer.writeheader()
        writer.writerows(lines)


if __name__ == "__main__":
    create_report()
