import time
import os
import threading
import logging

from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.console import Console
from rich.panel import Panel


from metrics.srpc_metrics_types import SrpcmetricsTypes


console = Console()
layout = Layout(name="root")

counter_metrics = {}
timer_metrics = {}

stop_event = threading.Event()
log_path = "srpc_server_metrics.log"
logger = logging.getLogger("srpc_show_metrics")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def increment_counter(metric_name):
    if metric_name not in counter_metrics:
        counter_metrics[metric_name] = 1
    else:
        counter_metrics[metric_name] += 1

def update_timer_metric(metric_name, value):
    if metric_name not in timer_metrics:
        timer_metrics[metric_name] = (value, value, value, value)  # min, max, total, avg
    else:
        min_val, max_val, total, avg = timer_metrics[metric_name]
        min_val = min(min_val, value)
        max_val = max(max_val, value)
        total += value
        procedure_name = metric_name.split(".")[0]
        count = counter_metrics.get(f"{procedure_name}.{SrpcmetricsTypes.COUNTER_SUCESS}", 0) + \
                counter_metrics.get(f"{procedure_name}.{SrpcmetricsTypes.COUNTER_FAIL}", 0)
        avg = total / count
        timer_metrics[metric_name] = (min_val, max_val, total, avg)

def generate_couter_table() -> Table:
    """Make a new table."""
    table = Table()
    table.add_column("metric")
    table.add_column("value")

    for metric_name, value in counter_metrics.items():
        metric_type = metric_name.split(".")[1]
        color = "green" if metric_type == SrpcmetricsTypes.COUNTER_SUCESS else "red"
        table.add_row(f"[{color}]{metric_name}[/]", f"[{color}]{value}[/]")

    return table

def generate_timer_table() -> Table:
    """Make a new table."""
    table = Table()
    table.add_column("procedure")
    table.add_column("min(ms)")
    table.add_column("max(ms)")
    table.add_column("total(ms)")
    table.add_column("avg(ms)")
    
    whatColor = False
    for metric_name, value in timer_metrics.items():
        whatColor = not whatColor
        procedure_name = metric_name.split(".")[0]
        min_val, max_val, total, avg = value
        color = "cyan" if whatColor==True else "magenta"
        table.add_row(f"[{color}]{procedure_name}[/]", f"[{color}]{min_val}[/]", \
                      f"[{color}]{max_val:.5f}[/]", f"[{color}]{total:.5f}[/]", f"[{color}]{avg:.5f}[/]")

    return table

def follow(thefile):
    thefile.seek(0, os.SEEK_END)
    
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue

        yield line


layout.split(
    Layout(name="header", size=3), 
    Layout(name="body", ratio=1),
)

layout["body"].split_row(
    Layout(name="left"),
    Layout(name="right")
)


layout["header"].update(Panel("SRPC Live Metrics Dashboard. Press Ctrl+C to exit.", style="bold white on blue"))
layout["left"].update(Panel("Counter Panel"))
layout["right"].update(Panel("Time Panel"))


try:
    # Live refresh
    with Live(layout, refresh_per_second=4, screen=True):
        logfile = open(log_path,"r")
        loglines = follow(logfile)
        for line in loglines:
            metric = line.split(" ")[4]
            metric_name = metric.split("=")[0]
            if (metric_name.split(".")[1] == SrpcmetricsTypes.COUNTER_FAIL) or \
                (metric_name.split(".")[1] == SrpcmetricsTypes.COUNTER_SUCESS):
                increment_counter(metric_name)
                panel = Panel(generate_couter_table(), title="Counter Panel")
                layout["left"].update(panel)
            else:
                value = float(metric.split("=")[1])
                update_timer_metric(metric_name, value)
                panel = Panel(generate_timer_table(), title="Time Panel")
                layout["right"].update(panel)
    stop_event.wait()
except KeyboardInterrupt:
    stop_event.set()
    logger.info("Exiting metrics dashboard.")