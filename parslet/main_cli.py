"""Command line interface entry point for Parslet.

This module exposes the ``cli`` and ``main`` functions which provide a small
command line tool to run workflows and perform a few convenience actions.
It is intended to be simple to keep the barrier to entry low for new users.
"""

import argparse
import sys

from parslet.security import offline_guard

from .plugins.loader import load_plugins
from .utils import get_parslet_logger


def cli() -> None:
    """Parse command line arguments and dispatch the chosen command."""
    parser = argparse.ArgumentParser(description="Parslet command line")
    if len(sys.argv) == 1:
        parser.print_help()
        return
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run", help="Run a workflow")
    run_p.add_argument("workflow")
    run_p.add_argument("--monitor", action="store_true", help="Show progress")
    run_p.add_argument("--battery-mode", action="store_true")
    run_p.add_argument("--json-logs", action="store_true")
    run_p.add_argument("--failsafe-mode", action="store_true")
    run_p.add_argument("--offline", action="store_true", help="Disable network access")
    run_p.add_argument(
        "--simulate",
        action="store_true",
        help="Show DAG and resources without executing",
    )
    run_p.add_argument("--no-cache", action="store_true", help="Disable task caching")
    run_p.add_argument(
        "--export-png",
        type=str,
        metavar="PATH",
        help="Export a PNG visualization of the DAG to the given path.",
    )

    rad_p = sub.add_parser("rad", help="Run RAD by Parslet example")
    rad_p.add_argument("image", nargs="?")
    rad_p.add_argument("--out-dir", default="rad_results")
    rad_p.add_argument("--simulate", action="store_true")

    conv_p = sub.add_parser("convert", help="Convert Parsl/Dask <-> Parslet scripts")
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

        wf = Path(args.workflow)
        if not Defcon.scan_code([wf]):
            logger.error("DEFCON1 rejection: unsafe code")
            return
        mod = load_workflow_module(str(wf))
        futures = mod.main()
        dag = DAG()
        dag.build_dag(futures)

        if args.export_png:
            try:
                dag.save_png(args.export_png)
                logger.info(f"DAG visualization saved to {args.export_png}")
            except Exception as e:
                logger.error(f"Failed to export DAG to PNG: {e}", exc_info=False)

        policy = None
        if args.battery_mode:
            policy = AdaptivePolicy(max_workers=2, battery_threshold=40)
        runner = DAGRunner(
            policy=policy,
            failsafe_mode=args.failsafe_mode,
            watch_files=[str(wf)],
            disable_cache=args.no_cache,
            json_logs=args.json_logs,
        )

        if args.simulate:
            print("--- DAG Simulation ---")
            print(dag.draw_dag())
            from parslet.utils.resource_utils import (
                get_available_ram_mb,
                get_battery_level,
            )

            ram = get_available_ram_mb()
            batt = get_battery_level()
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
        from parslet.compat.dask_adapter import (
            export_dask_dag,
            import_dask_script,
        )
        from parslet.compat.parsl_adapter import (
            export_parsl_dag,
            import_parsl_script,
        )

        if args.from_parsl and args.to_parslet:
            import_parsl_script(args.from_parsl, args.to_parslet)
            print(
                "Warning: experimental conversion; no staging, pure-Python bodies only",
                flush=True,
            )
        elif args.from_parslet and args.to_parsl:
            mod = load_workflow_module(args.from_parslet)
            futures = mod.main()
            export_parsl_dag(futures, args.to_parsl)
            print(
                "Warning: experimental conversion; no staging, pure-Python bodies only",
                flush=True,
            )
        elif args.from_dask and args.to_parslet:
            import_dask_script(args.from_dask, args.to_parslet)
            print(
                "Warning: experimental conversion; no staging, pure-Python bodies only",
                flush=True,
            )
        elif args.from_parslet and args.to_dask:
            mod = load_workflow_module(args.from_parslet)
            futures = mod.main()
            export_dask_dag(futures, args.to_dask)
            print(
                "Warning: experimental conversion; no staging, pure-Python bodies only",
                flush=True,
            )
        else:
            print(
                "Specify --from-parsl/--to-parslet, --from-parslet/--to-parsl,"
                " --from-dask/--to-parslet or --from-parslet/--to-dask",
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


def main() -> None:
    """Entry point used by the ``parslet`` console script."""
    cli()


if __name__ == "__main__":
    main()
