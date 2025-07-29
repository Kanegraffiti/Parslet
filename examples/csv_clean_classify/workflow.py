from pathlib import Path
import csv
from parslet.core import parslet_task, DAG, DAGRunner


@parslet_task
def load_csv(path: str):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = [r for r in reader if any(field.strip() for field in r)]
    return rows


@parslet_task
def classify(rows):
    return ["good" if len(r) > 2 else "bad" for r in rows]


@parslet_task
def save(rows, labels, out_dir: str):
    out = Path(out_dir)
    out.mkdir(exist_ok=True)
    out_csv = out / "clean.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for r, lab in zip(rows, labels):
            writer.writerow(r + [lab])
    return str(out_csv)


def main():
    data = load_csv("input.csv")
    labels = classify(data)
    out = save(data, labels, "csv_results")
    return [out]


if __name__ == "__main__":
    dag = DAG()
    dag.build_dag(main())
    runner = DAGRunner()
    runner.run(dag)
