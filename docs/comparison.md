# Parslet and Its Big Brothers (Parsl & Dask)

So you've heard of other tools like Parsl and Dask and you're wondering, "What's the difference? When should I use one over the other?"

That's a great question! Think of it like this:

-   **Parslet** is like a **sturdy, reliable bicycle**. It's perfect for getting you around your town (your single device), it works without any fuel (internet), and it's simple enough that anyone can learn to ride it.

-   **Parsl and Dask** are like **cargo ships and bullet trains**. They are incredibly powerful and designed to carry massive loads (huge amounts of data) across continents (multiple computers, servers, or the cloud). They're amazing, but they're also complex and need a lot of infrastructure to run.

The main idea is: **Parslet is built for simplicity and reliability on the device you have in your hand.** Parsl and Dask are built for massive power and scale on a whole network of computers.

### When to Ride Your Parslet Bicycle

Choose Parslet when:
- You need your recipe to run **offline**.
- You're working on a device with **limited battery**, like a phone, a tablet, or a Raspberry Pi.
- You want a simple tool that's **easy to install** and doesn't have a lot of complicated parts.
- You're just **starting to learn** about how to automate software recipes.

### When to Call in the Cargo Ships (Parsl & Dask)

You should think about "graduating" to Parsl or Dask when:
- You need to run your recipe on **many computers at once** (what they call a "cluster" or "the cloud").
- You're working with **so much data** that it won't even fit on your computer's memory.
- You need to connect to special, high-powered computers at a university or research lab (an "HPC environment").

### A Quick Look at the Family

Here’s a simple table to show the key differences.

| Feature           | Parslet (Your Bicycle)                        | Parsl (The Bullet Train)                      | Dask (The Cargo Ship)                          |
| ----------------- | --------------------------------------------- | --------------------------------------------- | ---------------------------------------------- |
| **Best For**      | Simple, offline recipes on your phone or Pi.  | Super-fast science experiments on big computers. | Analyzing huge amounts of data, like a giant spreadsheet. |
| **Where it Runs** | Right there on your device.                   | Can run on computers all over the world.      | Can also run on computers all over the world.  |
| **Setup**         | Super easy, no extra bits needed.             | Needs a special setup on the big computers.   | Also needs a special setup for big jobs.       |
| **How you write tasks** | With a friendly `@parslet_task` note.   | With `@python_app` or `@bash_app` notes.      | With `dask.delayed` or other special tools.    |

Parslet is the perfect place to start. You can build your recipe on your phone with Parslet, and if it ever needs to get really, *really* big, Parslet has tools to help you convert it to run on its big brothers, Parsl and Dask.