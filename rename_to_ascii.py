import argparse
import os, string
import unicodedata
from unidecode import unidecode


def ascii_equivalent(s: str) -> str:
    """Returns ASCII-characters-only representation of 's'.

    Non-ASCII characters are replaced with closest equivalent ASCII character.
    May introduce forbidden characters (for filenames), use
    `compatibility_substitution(s)` AFTER using this function to replace them.

    """
    s = unicodedata.normalize("NFKD", s)
    ascii_str = unidecode(s)

    # return without non-printable characters
    return "".join(c for c in ascii_str if c in string.printable)


forbidden_characters = {
    "windows": [
        ":",
        '"',
        "/",
        "\\",
        "<",
        ">",
        "|",
        "?",
        "*",
    ],
    "macos": [":", "/"],
    "unix": ["/"],
}


def compatibility_substitution(
    s: str,
    type: str = "windows",
    ascii_only: bool = False,
    colon: str = ";",
    double_quote: str = "'",
    fwd_slash: str = "-",
    backslash: str = "-",
    lt: str = "(lt)",
    gt: str = "(gt)",
    pipe: str = "-",
    question_mark: str = "(q)",
    asterisk: str = "^",
) -> str:
    """Replace characters in 's' to be compatible with 'type'.

    Occurences of a forbidden character will not be replaced (skipped) if its
    corresponding argument value is set to None. Set value to "" (empty string)
    to remove occurences of the character.

    Args:
        s (str): String to be fixed.
        type (str, optional): Type to make 's' compatible with. Determines
            which characters will be substituted. Options: "windows", "unix"
            or "macos". Defaults to "windows".
        ascii_only (bool, optional): Whether to only allow replacing with ASCII
            characters. Defaults to False.
        colon (str, optional): Character to replace ':'s with. Defaults to ";".
        double_quote (str, optional): Character to replace '"'s with. Defaults
            to "'".
        fwd_slash (str, optional): Character to replace '/'s with. Defaults
            to "-".
        backslash (str, optional): Character to replace backslash with. Defaults
            to "-".
        lt (str, optional): Character to replace '<'s with. Defaults to "(lt)".
        gt (str, optional): Character to replace '>'s with. Defaults to "(gt)".
        pipe (str, optional): Character to replace '|'s with. Defaults to "-".
        question_mark (str, optional): Character to replace '?'s with. Defaults
            to "(q)".
        asterisk (str, optional): Character to replace '*'s with. Defaults
            to "^".

    Returns:
        str: string which is 's' with forbidden characters replaced

    """
    complete_codemap = {
        ":": colon,
        '"': double_quote,
        "/": fwd_slash,
        "\\": backslash,
        "<": lt,
        ">": gt,
        "|": pipe,
        "?": question_mark,
        "*": asterisk,
    }

    try:
        relevant_keys = forbidden_characters[type.lower()]
    except KeyError:
        raise ValueError(f"type: invalid type: '{type}'")

    # codemap containing only the keys of characters to be replaced
    codemap = dict((key, complete_codemap[key]) for key in relevant_keys)

    # check replacement characters are valid
    for c, arg in codemap.items():
        if arg and arg in codemap.keys():
            raise ValueError(
                f"cannot replace with forbidden characters: '{c}' -> '{arg}'"
            )
        if arg and ascii_only and not arg.isascii():
            raise ValueError(
                f"cannot replace with non-ASCII characters: '{c}' -> '{arg}'"
            )

    # replace all forbidden character occurences with its substitute
    for char, replacement in codemap.items():
        if replacement:
            s = s.replace(char, replacement)

    return "".join(
        c for c in s if c in string.printable
    )  # return without non-printable characters


def filter_nonetypes(x: list) -> list:
    """Remove all None objects from list."""
    return [item for item in x if item]


def propose_changes(
    s: str, root: str = None, substitute_type: str = None
) -> tuple[str, str]:
    """
    Propose changes to make 's' contain only ASCII characters and compatible
    with 'substitute_type'.

    Args:
        s (str): String that changes will be proposed for.
        root (str, optional): Assumes 'root' and 's' forms a filepath if used,
            where 's' is the basename and 'root' should be kept intact. No
            changes will be proposed for 'root', but the return will use paths
            formed with 'root' rather than just 's'. Defaults to None.
        substitute_type (str, optional): Type to make 's' compatible with (as
            a filepath). Determines which characters will be substituted.
            Options: "windows", "unix" or "macos". Defaults to None.

    Returns:
        tuple[str, str]: tuple where the first element is the original string
            (or path), and the second is the proposed change

    """
    ascii_s = ascii_equivalent(s)

    if substitute_type:
        ascii_s = compatibility_substitution(ascii_s, substitute_type, True)

    if ascii_s == s:
        return None

    # if root, assume working with filepaths
    if root:
        return (os.path.join(root, s), os.path.join(root, ascii_s))

    return (s, ascii_s)


def _print_proposal(old: str, new: str, is_dir: bool = False) -> None:
    """Prints formatted proposal for renaming file/directory 'old' to 'new'.

    Args:
        old (str): Existing path.
        new (str): New path after renaming.
        is_dir (bool, optional): If renaming a directory (rather than file).
            Defaults to False.

    """
    path_type = "file"
    if is_dir:
        path_type = "dir"

    print(f"PROPOSAL ({path_type}): '{old}'")
    print(f"CHANGE (basename):")
    print(f"     {os.path.basename(old)}")
    print(f"     ->")
    print(f"     {os.path.basename(new)}")
    print()


def find_problem_filenames(
    path: str,
    substitute_type: bool = None,
    include_dirs: bool = True,
    recursive: bool = True,
) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """
    Finds pathnames under 'path' (if it is a directory) that includes
    non-ASCII or forbidden characters, and suggests new names. If 'path' is to
    a file, then suggests rename for just that one file.

    Args:
        path (str): Path to a directory (or file).
        substitute_type (bool, optional): Type to make pathnames compatible
            with. Determines which characters will be substituted. Options:
            "windows", "unix" or "macos". Defaults to None.
        include_dirs (bool, optional): Whether to check directory names as
            well as filenames. Defaults to True.
        recursive (bool, optional): Whether to include subdirectories
            (recursively). Defaults to True.

    Returns:
        tuple[list[tuple[str, str]], list[tuple[str, str]]]: Returns two
            lists, each containing tuples where the first element is an
            existing path, and the second element is the path after proposed
            renaming. The first list is for filenames, and the second is for
            directory names.

    """
    path = path.rstrip("/\\")

    if not os.path.exists(path):
        raise ValueError(f"'path' not found: '{path}'")

    problem_dirs = []
    problem_files = []

    root, basename = os.path.split(path)

    # if path is just a file
    if os.path.isfile(path):
        problem_files.append(propose_changes(basename, root, substitute_type))
        return filter_nonetypes(problem_files), problem_dirs

    # check directory at 'path', since it won't be part of walk
    if include_dirs:
        problem_dirs.append(propose_changes(basename, root, substitute_type))

    for root, dirs, files in os.walk(path):
        for file in files:
            problem_files.append(propose_changes(file, root, substitute_type))

        if include_dirs:
            for dir in dirs:
                problem_dirs.append(propose_changes(dir, root, substitute_type))

        if not recursive:
            break

    return filter_nonetypes(problem_files), filter_nonetypes(problem_dirs)


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
