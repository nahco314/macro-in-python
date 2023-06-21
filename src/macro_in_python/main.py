import argparse
from pathlib import Path

from macro_in_python.to_file import convert_file


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("source", type=str, help="Source file to convert.")
    parser.add_argument("output", type=str, help="Output file to write.")

    args = parser.parse_args()

    convert_file(Path(args.source), Path(args.output))

    print("Done.")


if __name__ == "__main__":
    main()
