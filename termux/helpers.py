"""
Parslet Termux Utilities
------------------------

This module provides helper functions specific to the Termux environment
on Android. These utilities can be used to detect if Parslet is running
within Termux, which might influence certain behaviors or feature availability
(e.g., access to specific Android features or adjusted default settings).
"""

import os
import logging

# Initialize a logger for this module.
logger = logging.getLogger(__name__)


def is_running_in_termux() -> bool:
    """
    Checks if the script is currently running within a Termux environment.

    The detection is primarily based on the presence and specific values of
    environment variables that are characteristic of Termux. These include:
    - `TERMUX_VERSION`: Set by Termux, indicating its version.
    - `PREFIX`: In Termux, this variable typically points to a specific path
      (`/data/data/com.termux/files/usr`).

    Returns:
        bool: True if the environment is identified as Termux, False otherwise.
    """
    # Check for the presence of the TERMUX_VERSION environment variable.
    # Its existence is a strong indicator of a Termux environment.
    termux_version = os.environ.get("TERMUX_VERSION")
    if termux_version is not None:
        logger.debug(f"Termux detected via TERMUX_VERSION: {termux_version}")
        return True

    # Check the value of the PREFIX environment variable.
    # In Termux, PREFIX is consistently set to '/data/data/com.termux/files/usr'.
    prefix_path = os.environ.get("PREFIX")
    if prefix_path == "/data/data/com.termux/files/usr":
        logger.debug(f"Termux detected via PREFIX path: {prefix_path}")
        return True

    # Additional checks could be added here if necessary, for example:
    # - Checking for specific files or directories unique to Termux.
    # - Querying system properties (though this might require platform-specific tools).
    # However, environment variables are generally the most straightforward and reliable method.

    logger.debug(
        "Termux environment not detected based on common environment variables."
    )
    return False


# This block allows for direct execution and testing of the functions in this module.
if __name__ == "__main__":
    # Basic logging setup for __main__ to see messages from this module.
    logging.basicConfig(
        level=logging.DEBUG
    )  # Set to DEBUG to see detection logs

    logger.info("--- Termux Helper Test ---")

    running_in_termux = is_running_in_termux()

    if running_in_termux:
        logger.info(
            "Detection result: This script appears to be running inside Termux."
        )
    else:
        logger.info(
            "Detection result: This script does NOT appear to be running inside Termux."
        )

    # Print relevant environment variables for diagnostic purposes during testing.
    logger.info("\nRelevant environment variables for diagnostics:")
    for var in [
        "TERMUX_VERSION",
        "PREFIX",
        "HOME",
        "SHELL",
        "USER",
        "PATH",
        "ANDROID_ROOT",
        "ANDROID_DATA",
    ]:
        logger.info(f"  {var}: {os.environ.get(var)}")

    logger.info("--- End of Test ---")
