"""Command line interface entry point for Parslet.

This module exposes the ``cli`` and ``main`` functions which provide a small
command line tool to run workflows and perform a few convenience actions.
It is intended to be simple to keep the barrier to entry low for new users.
"""

import argparse
import json
import sys

from parslet.security import offline_guard

from .plugins.loader import load_plugins
from .utils import get_parslet_logger


def cli() -> None:
    """Parse command line arguments and dispatch the chosen command."""
    desc = "Parslet command line - run and convert workflows."
    parser = argparse.ArgumentParser(
        description=desc,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    if len(sys.argv) == 1:
        parser.print_help()
        return
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser(
        "run",
        help="Run a workflow",
        description="Execute a Parslet workflow file or module reference.",
    )
    run_p.add_argument(
        "workflow",
        help="Workflow file path or module:func reference",
    )
    run_p.add_argument(
        "--monitor",
        action="store_true",
        help="Show live task progress during execution",
    )
    run_p.add_argument(
        "--battery-mode",
        action="store_true",
        help="Limit workers when system battery is low",
    )
    run_p.add_argument(
        "--json-logs",
        action="store_true",
        help="Emit logs in JSON format",
    )
    run_p.add_argument(
        "--failsafe-mode",
        action="store_true",
        help="Continue running even if some tasks fail",
    )
    run_p.add_argument(
        "--offline",
        action="store_true",
        help="Disable network access",
    )
    run_p.add_argument(
        "--simulate",
        action="store_true",
        help="Show DAG and resources without executing",
    )
    run_p.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable task caching",
    )
    run_p.add_argument(
        "--max-workers",
        type=int,
        help="Maximum number of worker threads",
    )
    run_p.add_argument(
        "--export-png",
        type=str,
        metavar="PATH",
        help="Export a PNG visualization of the DAG to PATH",
    )
    run_p.add_argument(
        "--export-stats",
        type=str,
        metavar="PATH",
        help="Write task execution stats to the given JSON file",
    )

    rad_p = sub.add_parser("rad", help="Run RAD by Parslet example")
    rad_p.add_argument("image", nargs="?")
    rad_p.add_argument("--out-dir", default="rad_results")
    rad_p.add_argument("--simulate", action="store_true")

    conv_help = "Convert Parsl/Dask <-> Parslet scripts"
    conv_p = sub.add_parser("convert", help=conv_help)
    conv_p.add_argument("--from-parsl", metavar="PATH")
    conv_p.add_argument("--to-parslet", metavar="PATH")
    conv_p.add_argument("--from-parslet", metavar="PATH")
    conv_p.add_argument("--to-parsl", metavar="PATH")
    conv_p.add_argument("--from-dask", metavar="PATH")
    conv_p.add_argument("--to-dask", metavar="PATH")

    sub.add_parser("test", help="Run tests")
    sub.add_parser("diagnose", help="Show system info")
    sub.add_parser("examples", help="List examples")

    args = parser.parse_args()
    logger = get_parslet_logger("parslet-cli")
    load_plugins()
    logger.info("Plugins loaded")

    try:
        if args.cmd == "run":
            import threading
            import time
            from pathlib import Path

            from rich.live import Live
            from rich.table import Table

            from parslet.cli import load_workflow_module
            from parslet.core import DAG, DAGRunner
            from parslet.core.policy import AdaptivePolicy
            from parslet.security.defcon import Defcon

            wf_input = args.workflow
            mod = load_workflow_module(wf_input)
            wf = Path(mod.__file__ or "")
            if wf and not Defcon.scan_code([wf]):
                logger.error("DEFCON1 rejection: unsafe code")
                return
            futures = mod.main()
            dag = DAG()
            dag.build_dag(futures)

            if getattr(mod, "__converted_from_parsl__", False):
                from parslet.compat.parsl_adapter import export_parsl_dag

                orig = Path(getattr(mod, "__original_parsl_path__"))
                export_name = f"{orig.stem}_parslet_export.py"
                export_path = orig.with_name(export_name)
                try:
                    export_parsl_dag(futures, str(export_path))
                    msg = "Parsl export written to " + f"{export_path}"
                    logger.info(msg)
                except Exception as e:
                    logger.error(
                        f"Could not export Parsl workflow: {e}", exc_info=False
                    )

            if args.export_png:
                try:
                    dag.save_png(args.export_png)
                    msg = "DAG visualization saved to " + f"{args.export_png}"
                    logger.info(msg)
                except Exception as e:
                    err = f"Failed to export DAG to PNG: {e}"
                    logger.error(err, exc_info=False)

            policy = None
            if args.battery_mode:
                policy = AdaptivePolicy(max_workers=2, battery_threshold=40)
            runner = DAGRunner(
                policy=policy,
                failsafe_mode=args.failsafe_mode,
                watch_files=[str(wf)] if wf else None,
                disable_cache=args.no_cache,
                json_logs=args.json_logs,
                max_workers=args.max_workers,
            )

            if args.simulate:
                print("--- DAG Simulation ---")
                print(dag.draw_dag())
                from parslet.utils import resource_utils

                ram = resource_utils.get_available_ram_mb()
                batt = resource_utils.get_battery_level()
                if ram is not None:
                    print(f"Available RAM: {ram:.1f} MB")
                if batt is not None:
                    print(f"Battery level: {batt}%")
                return

            if args.monitor:

                def _run() -> None:
                    with offline_guard(args.offline):
                        runner.run(dag)

                t = threading.Thread(target=_run)
                t.start()
                with Live(refresh_per_second=4) as live:
                    while t.is_alive():
                        table = Table()
                        table.add_column("Task")
                        table.add_column("Status")
                        for tid, status in runner.task_statuses.items():
                            table.add_row(tid, status)
                        live.update(table)
                        time.sleep(0.5)
                    t.join()
                    table = Table()
                    table.add_column("Task")
                    table.add_column("Status")
                    for tid, status in runner.task_statuses.items():
                        table.add_row(tid, status)
                    live.update(table)
            else:
                with offline_guard(args.offline):
                    runner.run(dag)
                if args.export_stats:
                    try:
                        stats_path = args.export_stats
                        with open(stats_path, "w", encoding="utf-8") as fh:
                            json.dump(
                                {
                                    "task_statuses": runner.task_statuses,
                                    "task_execution_times": (
                                        runner.task_execution_times
                                    ),
                                },
                                fh,
                                indent=2,
                            )
                        msg = "Stats written to " + f"{args.export_stats}"
                        logger.info(msg)
                    except Exception as e:  # pragma: no cover - defensive
                        err = f"Failed to export stats: {e}"
                        logger.error(err, exc_info=False)
        elif args.cmd == "rad":
            from examples.rad_parslet.rad_dag import main as rad_main
            from parslet.core import DAG, DAGRunner

            futures = rad_main(args.image, args.out_dir)
            dag = DAG()
            dag.build_dag(futures)

            if args.simulate:
                print("--- RAD DAG Simulation ---")
                print(dag.draw_dag())
                return

            runner = DAGRunner()
            runner.run(dag)

        elif args.cmd == "convert":
            from parslet.cli import load_workflow_module
            from parslet.compat import dask_adapter, parsl_adapter

            if args.from_parsl and args.to_parslet:
                parsl_adapter.import_parsl_script(
                    args.from_parsl,
                    args.to_parslet,
                )
                print(
                    "Warning: experimental conversion; no staging, "
                    "pure-Python bodies only",
                    flush=True,
                )
            elif args.from_parslet and args.to_parsl:
                mod = load_workflow_module(args.from_parslet)
                futures = mod.main()
                parsl_adapter.export_parsl_dag(futures, args.to_parsl)
                print(
                    "Warning: experimental conversion; no staging, "
                    "pure-Python bodies only",
                    flush=True,
                )
            elif args.from_dask and args.to_parslet:
                dask_adapter.import_dask_script(
                    args.from_dask,
                    args.to_parslet,
                )
                print(
                    "Warning: experimental conversion; no staging, "
                    "pure-Python bodies only",
                    flush=True,
                )
            elif args.from_parslet and args.to_dask:
                mod = load_workflow_module(args.from_parslet)
                futures = mod.main()
                dask_adapter.export_dask_dag(futures, args.to_dask)
                print(
                    "Warning: experimental conversion; no staging, "
                    "pure-Python bodies only",
                    flush=True,
                )
            else:
                print(
                    "Specify --from-parsl/--to-parslet, "
                    "--from-parslet/--to-parsl, --from-dask/--to-parslet "
                    "or --from-parslet/--to-dask",
                    flush=True,
                )
        elif args.cmd == "test":
            import pytest

            pytest.main(["-q", "tests"])
        elif args.cmd == "diagnose":
            from .utils.diagnostics import find_free_port

            print("Free port:", find_free_port())
        elif args.cmd == "examples":
            from pathlib import Path

            for f in Path("use_cases").glob("*.py"):
                print(f.name)
    except Exception as exc:  # pragma: no cover - friendly error surface
        logger.error(f"An error occurred: {exc}", exc_info=False)


def main() -> None:
    """Entry point used by the ``parslet`` console script."""
    cli()


if __name__ == "__main__":
    main()
