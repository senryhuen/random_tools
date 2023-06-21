import argparse
import string
import unicodedata
from unidecode import unidecode


def ascii_equivalent(s: str) -> str:
    """Returns ASCII-characters-only representation of 's'."""
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
