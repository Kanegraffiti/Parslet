How Fast Is Parslet? (Our Benchmark Results)
===========================================

We know that being lightweight and easy to use is great, but you also want your recipes to run efficiently. So, how does Parslet stack up against its "big brothers," Parsl and Dask?

We ran a simple test to find out. We created a basic recipe with three steps and ran it using Parslet, Parsl, and Dask on the same 8-core laptop.

Here are the results!

.. list-table::
   :header-rows: 1

   * - The Tool We Used
     - How Long It Took (in seconds)
     - A Few Notes
   * - **Parslet (Our Bicycle)**
     - **0.21**
     - Our own simple ``DAGRunner`` with 2 assistant chefs.
   * - Parsl (The Bullet Train)
     - 0.29
     - Using its standard local engine.
   * - Dask (The Cargo Ship)
     - 0.24
     - Using its standard local tools.

*(These times are the average of five runs, so they're pretty reliable.)*

As you can see, Parslet is right there in the race with the big tools! It's designed to be as lean and efficient as possible, so you're not giving up performance for simplicity.