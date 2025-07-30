import string
import json
from typing import List, Dict
from parslet.core import parslet_task, ParsletFuture, DAG, DAGRunner
from parslet.core.exporter import save_dag_to_png


@parslet_task
def load_text_file(file_path: str) -> str:
    """Reads text from a file and returns its content."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Text file not found at {file_path}")
        raise
    except Exception as e:
        print(f"Error loading text file {file_path}: {e}")
        raise


@parslet_task
def remove_punctuation(text: str) -> str:
    """Removes common punctuation marks from the text."""
    if text is None:
        print("Error: Input text to remove_punctuation is None.")
        raise ValueError("Input text to remove_punctuation is None.")
    try:
        # Using string.punctuation to get a comprehensive list of punctuation marks
        translator = str.maketrans("", "", string.punctuation)
        return text.translate(translator)
    except Exception as e:
        print(f"Error removing punctuation: {e}")
        raise


@parslet_task
def convert_to_lowercase(text: str) -> str:
    """Converts all characters in the text to lowercase."""
    if text is None:
        print("Error: Input text to convert_to_lowercase is None.")
        raise ValueError("Input text to convert_to_lowercase is None.")
    try:
        return text.lower()
    except Exception as e:
        print(f"Error converting text to lowercase: {e}")
        raise


@parslet_task
def count_words(text: str) -> Dict[str, int]:
    """Counts the frequency of each word and returns a dictionary."""
    if text is None:
        print("Error: Input text to count_words is None.")
        raise ValueError("Input text to count_words is None.")
    try:
        words = text.split()
        word_counts: Dict[str, int] = {}
        for word in words:
            if (
                word
            ):  # Ensure empty strings from multiple spaces are not counted
                word_counts[word] = word_counts.get(word, 0) + 1
        return word_counts
    except Exception as e:
        print(f"Error counting words: {e}")
        raise


@parslet_task
def save_word_counts(word_counts: Dict[str, int], output_path: str) -> None:
    """Saves the word counts as JSON to the specified path."""
    if word_counts is None:
        print("Error: Input word_counts to save_word_counts is None.")
        raise ValueError("Input word_counts to save_word_counts is None.")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(word_counts, f, indent=4)
        print(f"Word counts saved to {output_path}")
    except IOError as e:
        print(f"I/O Error saving word counts to {output_path}: {e}")
        raise
    except Exception as e:
        print(f"Error saving word counts to {output_path}: {e}")
        raise


def main() -> List[ParsletFuture]:
    """Defines the text cleaning DAG and returns terminal futures."""
    input_text_path = "input.txt"  # Dummy input text file path

    # Define the DAG
    text_content_future = load_text_file(input_text_path)
    lowercase_future = convert_to_lowercase(text_content_future)
    no_punctuation_future = remove_punctuation(lowercase_future)
    word_counts_future = count_words(no_punctuation_future)
    save_op_future = save_word_counts(word_counts_future, "word_counts.txt")

    return [save_op_future]


if __name__ == "__main__":
    print("Parslet Text Cleaner Example")
    print("----------------------------")
    print(
        "This script defines a DAG to load a text file, clean it (lowercase, remove punctuation),"
    )
    print("count word frequencies, and save the results to 'word_counts.txt'.")
    print("\nIMPORTANT:")
    print(
        "To run this example, you need to create a dummy input file named 'input.txt'"
    )
    print(
        "in the same directory as this script. Populate it with some sample text."
    )
    print("For example:")
    print(
        "  Hello world! This is a test. This is, indeed, a test file for Parslet."
    )
    print("----------------------------\n")

    entry_futures = main()

    # Build and run the DAG
    dag = DAG(entry_futures)
    print("DAG built. Visualizing DAG...")
    save_dag_to_png(dag, "text_cleaner_dag.png")
    print("DAG visualization saved to text_cleaner_dag.png")

    print("\nRunning DAG...")
    # Using a default number of workers, can be adjusted
    runner = DAGRunner(dag)
    results = runner.run()

    print("\nDAG Execution Results:")
    for future, result_info in results.items():
        if (
            future in entry_futures
        ):  # We are typically interested in terminal nodes
            print(f"  Task {future.name} (Terminal Node):")
            print(f"    Status: {result_info['status']}")
            if result_info["status"] == "completed":
                print("    Output Path (if applicable): word_counts.txt")
            elif result_info["status"] == "failed":
                print(f"    Error: {result_info['error']}")
            elif result_info["status"] == "skipped":
                print("    Reason: A dependency failed.")

    print("\nText cleaning workflow execution finished.")
    if all(
        res["status"] == "completed"
        for future, res in results.items()
        if future in entry_futures
    ):
        print(
            "Output 'word_counts.txt' should be generated if all tasks succeeded."
        )
    else:
        print(
            "One or more tasks failed. 'word_counts.txt' might not be generated or complete."
        )
