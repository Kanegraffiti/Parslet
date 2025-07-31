# Parslet: Offline-First Workflow Automation for Low-Resource Devices

## Problem Definition and Context

A lot of workflow automation tools today (like Airflow or Prefect) are designed for big machines or cloud servers. But what happens when someone only has access to an Android phone, a low-end laptop, or a Raspberry Pi — especially in places where power is unreliable and internet is expensive or unstable?

That’s where Parslet comes in. I built it because I wanted something that could:

- Run **without internet**
- Be **gentle on battery and RAM**
- Work on **Android via Termux**, Linux, or even other small devices
- Still give people **powerful tools** like DAGs and resource-aware scheduling

Parslet is my answer — a mini framework inspired by Parsl and Dask, but stripped down and rebuilt to be usable *anywhere*.

---

## Identified Constraints

These were the real problems I had to think about from the start:

- **Power supply**: Inconsistent electricity means workflows should be short, interruptible, and battery-conscious
- **Data costs**: Internet is not always available or affordable, so everything has to run locally
- **Compute limits**: Phones and low-end PCs don’t have much RAM or CPU, so tasks need to adapt
- **Connectivity**: No reliance on cloud syncs, distributed clusters, or external APIs

---

## Design Alternatives and Final Decisions

At first, I thought about extending Parsl directly, but it’s built with a lot of assumptions about HPC setups and Jupyter environments. So I tried:

- **Option 1:** Strip down Parsl to work offline — too brittle
- **Option 2:** Rewrite a DAG engine with task decorators — better control
- **Option 3:** Add resource checks before running — perfect fit for mobile

In the end, Parslet has:

- A **task decorator** (`@parslet_task`) that turns any function into a node in the DAG
- A **runner** that checks available RAM and battery before executing
- A **plugin system** so users can add custom tools (e.g., for audio, image, or CSV workflows)
- A simple **CLI** that runs DAGs and logs everything clearly
- **DEFCON** — an internal sentinel system that validates the system, the DAG, and any imported files for safety

---

## Tools and Technologies Used

| Tool | Why I Chose It |
|------|----------------|
| **Python** | Cross-platform, easy to write, great for DAGs |
| **Termux** | Lets Android run like Linux — perfect for mobile workflows |
| **Pillow, OpenCV, pandas** | To support media and data tasks |
| **Git + GitHub** | For version control and documentation |
| **Markdown + ReadTheDocs** | Easy-to-navigate docs, works offline too |
| **Gemini CLI** | Used locally to improve code and write automation |
| **Codex** | For rewriting and debugging core logic when stuck |

No external AI is bundled in Parslet. All training, suggestions, and fixes were tested offline and hardcoded where necessary.

---

## Performance Tests and Benchmarks

Testing was done on:

- **Device**: Lenovo TB128FU tablet with 6GB RAM and Android 12
- **Environment**: Termux, Python 3.12
- **Benchmark Tasks**: image filtering, CSV cleaning, audio splitting

| Task | Runtime | RAM Used | Battery Drop |
|------|---------|----------|---------------|
| Image Filter DAG | ~1.8s | ~30MB | ~1% over 3 runs |
| CSV Cleanup DAG | ~2.2s | ~20MB | ~1% |
| Audio Cutter (MP3) | ~4.1s | ~45MB | ~2% |

All tests passed even in **battery-saving mode** and with background processes open. Parslet gracefully skips tasks if resources are too low, and provides human-readable error messages.

---

## Final Notes

I’m proud of how far Parslet has come. It’s not a giant framework, it’s a small, tough, portable tool for people who don’t have access to high-end infrastructure but still want to do powerful things.

And it’s 100% open source. I built this so that one day, anyone with just a phone can automate workflows, clean data, and run AI without asking permission from the cloud.

My aim is to put powerful tools into more hands.
