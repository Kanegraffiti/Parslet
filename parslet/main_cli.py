"""Command line interface entry point for Parslet.

This module exposes the ``cli`` and ``main`` functions which provide a small
command line tool to run workflows and perform a few convenience actions.
It is intended to be simple to keep the barrier to entry low for new users.
"""

import argparse
import sys
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
    run_p.add_argument("--failsafe-mode", action="store_true")
    run_p.add_argument(
        "--simulate",
        action="store_true",
        help="Show DAG and resources without executing",
    )
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

    conv_p = sub.add_parser("convert", help="Convert Dask or Parsl scripts")
    grp = conv_p.add_mutually_exclusive_group(required=True)
    grp.add_argument("--from-parsl", dest="from_parsl", action="store_true")
    grp.add_argument("--from-dask", dest="from_dask", action="store_true")
    grp.add_argument("--to-parsl", dest="to_parsl", action="store_true")
    conv_p.add_argument("script")

    sub.add_parser("test", help="Run tests")
    sub.add_parser("diagnose", help="Show system info")
    sub.add_parser("examples", help="List examples")

    args = parser.parse_args()
    logger = get_parslet_logger("parslet-cli")
    load_plugins()
    logger.info("Plugins loaded")

    if args.cmd == "run":
        from pathlib import Path
        from parslet.security.defcon import Defcon
        from parslet.cli import load_workflow_module
        from parslet.core import DAG, DAGRunner
        from rich.table import Table
        from rich.live import Live
        import threading
        import time

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
                logger.error(
                    f"Failed to export DAG to PNG: {e}", exc_info=False
                )

        runner = DAGRunner(
            battery_mode_active=args.battery_mode,
            failsafe_mode=args.failsafe_mode,
            watch_files=[str(wf)],
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

            def _run():
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
            runner.run(dag)
    elif args.cmd == "rad":
        from parslet.core import DAG, DAGRunner
        from examples.rad_parslet.rad_dag import main as rad_main

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
        from pathlib import Path

        if args.to_parsl:
            from parslet.compat import convert_parslet_to_parsl as conv

            suffix = "_parsl.py"
        elif args.from_parsl:
            from parslet.compat import convert_parsl_to_parslet as conv

            suffix = "_parslet.py"
        else:
            from parslet.compat import convert_dask_to_parslet as conv

            suffix = "_parslet.py"

        code = Path(args.script).read_text()
        new_code = conv(code)
        out = Path(args.script).with_name(Path(args.script).stem + suffix)
        out.write_text(new_code)
        print(f"Converted file saved as {out}")
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
