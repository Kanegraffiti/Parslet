Real-World Use Cases
====================

This page highlights real-world applications where Parslet excels, particularly in environments with limited connectivity and resources. These examples are inspired by challenges like the IHS Power Management Challenge.

.. contents::
   :local:

Remote Telecom Tower Monitoring
-------------------------------

**The Problem:** Telecom towers in remote locations often rely on hybrid power systems (solar, battery, generator). Monitoring these systems to predict maintenance needs is critical for preventing downtime, but is challenging due to unreliable network connectivity.

**Why Parslet is a Good Fit:**
*   **Offline-First:** Parslet workflows run entirely on-device (e.g., a Raspberry Pi at the tower), analyzing logs without needing a cloud connection.
*   **Resource-Aware:** It runs efficiently on low-power hardware without draining the site's critical power reserves.
*   **Automated Analysis:** A Parslet DAG can automate the daily process of ingesting logs, analyzing trends, and generating actionable maintenance alerts.

**Running the Example:**

The ``telecom_power_monitor.py`` use case simulates this scenario.

1.  **Create a sample log file.** In the project root, create a file named ``tower_power.csv`` with the following content:

    .. code-block:: text

       battery,generator_hours,solar_kw
       48.5,1.2,3.5
       45.1,2.5,3.2
       38.9,4.0,2.1
       49.0,0.5,4.0

2.  **Run the workflow:**

    .. code-block:: bash

       parslet run use_cases/telecom_power_monitor.py

3.  **Check the results:** A new directory will be created in ``Parslet_Results/`` containing a ``tower_report.json`` file with the analysis and recommended actions.

Solar Site Optimization
-----------------------

**The Problem:** For hybrid systems involving solar power, optimizing maintenance (like panel cleaning) is key to maximizing efficiency. This requires analyzing historical power output data to detect degradation, a task that must often be done on-site with local, low-power devices.

**Why Parslet is a Good Fit:**
*   **Edge Analytics:** Parslet can run data analysis workflows directly on an edge device at the solar site.
*   **Simple Scheduling:** The DAG defines a clear, repeatable process: load data, analyze efficiency, and generate a maintenance schedule.
*   **Battery-Aware:** For battery-powered monitoring hardware, Parslet's ``--battery-mode`` ensures that analysis tasks don't exhaust the power supply.

**Running the Example:**

The ``solar_scheduling.py`` use case demonstrates this.

1.  **Create a sample data file.** In the project root, create a file named ``power.csv`` with some sample power output values:

    .. code-block:: text

       85.5
       82.1
       75.9
       68.0
       65.5

2.  **Run the workflow:**

    .. code-block:: bash

       parslet run use_cases/solar_scheduling.py

3.  **Check the results:** A new directory will be created in ``Parslet_Results/`` containing a ``schedule.json`` file with the average efficiency and a recommended action (e.g., "clean" or "ok").
