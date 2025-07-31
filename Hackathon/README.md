# Parslet: Africa DevTech Hackathon Submission

## Project Name
Parslet

## Executive Summary
Parslet is a lightweight, offline-first Python workflow engine designed to automate complex tasks on resource-constrained devices, such as Android phones and Raspberry Pis. It empowers developers, technicians, and innovators across Africa to build and run professional-grade automation anywhere, regardless of internet connectivity or hardware limitations. By bringing the power of workflow automation to the edge, Parslet bridges the gap between brilliant ideas and the tools needed to realize them in challenging environments.

## The Problem
Professional software development and automation tools are overwhelmingly designed for cloud environments, assuming powerful hardware, stable power, and constant, high-speed internet access. This paradigm creates a significant barrier for a vast number of users in Africa who operate where these resources are not guaranteed, effectively excluding them from leveraging modern automation. The tools of the cloud are not built for the edge.

## Our Solution: A Professional Tool for the Edge
Parslet is our answer. It is a small, smart, and robust Python tool that brings powerful workflow automation to the devices people already have. With Parslet, a developer can build, test, and run a sophisticated, multi-step workflow on a basic Android phone or a Raspberry Pi, completely offline. It is engineered for reliability and efficiency, enabling professional-grade automation in the most demanding and resource-scarce environments.

## Core Features
Parslet is engineered for reliability and efficiency in challenging environments:

-   **Offline-First Execution:** All workflows run entirely on-device, making Parslet perfect for remote or disconnected locations.
-   **Battery-Aware Scheduling:** The `--battery-mode` flag enables an intelligent scheduler that conserves energy by automatically reducing concurrency, ensuring critical tasks can complete on battery power.
-   **Adaptive Resource Management:** Parslet dynamically adapts to the host device's CPU and memory, preventing crashes and ensuring smooth operation even on low-power hardware.
-   **Seamless Scalability:** We provide a clear path from prototype to production. Workflows developed on Parslet can be seamlessly converted to run on industrial-strength engines like Parsl and Dask for cloud-scale execution.
-   **Built-in Security:** A multi-level "DEFCON" security system scans code for vulnerabilities and protects against common errors, ensuring workflow integrity.

## Solution for the IHS Power Management Challenge
Parslet is uniquely suited to solve the core issues of the IHS Power Management Challenge by enabling on-site, automated monitoring and analysis of power systems at remote telecom towers.

**Use Case: Predictive Maintenance for Telecom Towers**

A Parslet workflow deployed on a low-power computer (e.g., a Raspberry Pi) at a telecom tower can:

1.  **Automate Log Analysis:** Ingest and process daily logs from hybrid power systems (solar, battery, generator) entirely offline.
2.  **Predict Maintenance Needs:** Analyze trends in battery health, generator runtime, and solar output to proactively identify issues like a degrading battery or excessive generator usage before they cause a failure.
3.  **Operate on Low Power:** The engine's battery- and resource-aware features ensure it runs reliably without draining the site's critical power reserves.
4.  **Generate Actionable Reports:** Create concise maintenance alerts (e.g., "Inspect generator," "Schedule battery replacement") that are stored locally and synchronized to a central server only when a network connection is available.

By deploying Parslet, IHS can transition from reactive to predictive maintenance, significantly reducing downtime, optimizing power consumption, and lowering operational costs across its network of remote towers.

## Demonstration
![Battery Aware Demo](docs/visuals/battery_aware_demo.jpg)
The `battery_aware_demo.py` script in this directory provides a practical demonstration of a power-sensitive workflow, showcasing how tasks adapt their behavior based on the device's battery level.
