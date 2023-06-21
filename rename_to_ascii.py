import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", type=str, help="filepath to a file or directory")
    parser.add_argument(
        "-c",
        "--compatibility",
        metavar="'type'",
        type=str,
        default=None,
        help="substitute forbidden characters to be compatible with 'windows', 'macos' or 'unix' (default: None)",
    )
    parser.add_argument(
        "-n",
        "--no-rename",
        action="store_true",
        help="do not attempt to rename, just output proposed changes (default: False)",
    )
    parser.add_argument(
        "-y",
        "--skip-confirmation",
        action="store_true",
        help="rename without asking for confirmation (default: False)",
    )
    parser.add_argument(
        "-xd",
        "--exclude-directories",
        action="store_true",
        help="do not rename directories (default: False)",
    )
    parser.add_argument(
        "-f",
        "--flat",
        action="store_true",
        help="do not recursively include files in subdirectories (default: False)",
    )

    args = parser.parse_args()


if __name__ == "__main__":
    main()
