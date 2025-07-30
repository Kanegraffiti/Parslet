# What Happens When Things Go Wrong?

Even the best-laid plans can have a hiccup! This guide explains how Parslet helps you deal with common errors and keeps your recipes running smoothly.

### Learning from the Big Kids (Parsl & Dask)

Parslet's "big brothers," Parsl and Dask, are super powerful, but sometimes they can run into tricky situations. We learned from their experiences and built Parslet to automatically handle some of these for you.

For example, sometimes with Parsl, running several recipes one after another could get things stuck. Parslet fixes this by making sure every recipe gets its own clean workspace. We also turned off some of the complicated tracking features by default to make sure your recipes can start and stop cleanly every time.

### A Few Tips for Healthy Recipes

Here are a few simple tips to make your Parslet recipes extra robust.

-   **Wrap Your Tasks in a "Try" Block:** If you have a task that might fail (for example, trying to download a file), it's a good idea to wrap your code in a `try...except` block. This is like telling Python, "Try to do this, but if it doesn't work, don't crash! Just do this other thing instead."

-   **Check the Report Card:** After a recipe runs, you can use `DAGRunner.get_task_benchmarks()` to see a "report card" for all your tasks. It will show you which ones succeeded, which ones failed, and how long they took. It's a great way to see what's going on!

-   **Save Your Progress!** This is a big one. If you're running a long recipe, use the `--checkpoint-file <some_file_name.json>` command. This tells Parslet to write down every step it finishes. If your recipe gets interrupted (maybe your battery dies or you lose your connection), you can just run it again with the same command. Parslet will read the file and pick up right where it left off, skipping all the steps that were already done.

-   **Network Detective:** Parslet is smart enough to check if you have an internet connection. If it sees you're offline or that you're using a VPN, it will print a friendly warning. This can be a lifesaver for figuring out why a task that needs the internet might have failed!