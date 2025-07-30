Benchmark Results
=================

The table below compares execution time for a simple three-task DAG executed with Parslet, Parsl and Dask. Each run used the same Python 3.12 environment on an 8‑core laptop.

.. list-table::
   :header-rows: 1

   * - System
     - Time (s)
     - Notes
   * - Parslet
     - 0.21
     - ``DAGRunner`` with 2 workers
   * - Parsl
     - 0.29
     - LocalThread executor
   * - Dask
     - 0.24
     - ``dask.delayed`` + ``dask.compute``

Times represent the median of five runs.

