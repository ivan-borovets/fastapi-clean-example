import argparse
import shutil
import tempfile
from enum import StrEnum
from pathlib import Path

BASE_DIR: Path = Path(__file__).parent.parent.parent
POSTGRES_HOST: str = "POSTGRES_HOST"
LOCALHOST: str = "localhost"


class Modes(StrEnum):
    local = "local"
    docker = "docker"


def identify_lines(path: Path, mode: Modes) -> dict[int, str]:
    target_lines: dict[int, str] = {}

    with open(path, "r", encoding="utf-8") as file:
        for line_idx, line in enumerate(file):
            if POSTGRES_HOST not in line:
                continue

            if mode is Modes.local:
                if LOCALHOST in line:
                    new_line = f'{POSTGRES_HOST} = "{LOCALHOST}"'
                else:
                    new_line = f'#{line.rstrip().strip("#")}'
            elif mode is Modes.docker:
                if LOCALHOST in line:
                    new_line = f'#{POSTGRES_HOST} = "{LOCALHOST}"'
                else:
                    _, target, after = line.partition(POSTGRES_HOST)
                    new_line = f'{target}{after.rstrip()}'

            target_lines.setdefault(line_idx, new_line)
    return target_lines


def replace_lines(path: Path, donor: dict[int, str]) -> None:
    _, temp_path = tempfile.mkstemp()

    with open(path, "r", encoding="utf-8") as source_file:
        with open(temp_path, "w", encoding="utf-8") as new_file:
            for line_idx, line in enumerate(source_file):
                if line_idx in donor:
                    new_file.write(f"{donor[line_idx]}\n")
                else:
                    new_file.write(line)

    shutil.move(temp_path, path)
    print(f"Lines were replaces in {path} ✨")
    return


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Replace lines in config file based on the mode"
    )
    parser.add_argument(
        "mode",
        type=str,
        choices=list(Modes),
        help="Mode of operation: 'local' / 'docker'",
    )
    args = parser.parse_args()
    selected_mode = Modes(args.mode)
    cfg_toml_path: Path = BASE_DIR / "config.toml"
    donor = identify_lines(cfg_toml_path, selected_mode)
    replace_lines(cfg_toml_path, donor)
    return


if __name__ == "__main__":
    main()
