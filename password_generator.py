"""Password Generator

This script will generate a random password of a chosen length and complexity.
There is an option to include special characters (punctuation) or just use
alphanumeric characters. Any selection of characters can be excluded aswell.

The default configuration is to generate a password of 16 characters, and
using special characters.

This script has no external dependencies.

Contains the following functions:
    * generate_password - generates a password with options/constraints
        defined by args given
    * main - main function which parses command line arguments into arguments
        to run generate_password with

"""

import argparse
import random
import string


full_character_set = string.digits + string.ascii_letters + string.punctuation
alphanumeric_character_set = string.digits + string.ascii_letters


def generate_password(
    pw_length: int,
    alphanumeric_characters_only: bool = False,
    excluded_characters: list = [],
) -> str:
    """Generates and returns a random password

    Generates a random password by creating a string of characters randomly
    selected from a character set (characters can be used more than once).

    The default character sets are alphanumeric (letters and numbers) or
    alphanumeric with special characters (letters, numbers and punctuation).
    The character sets can be modified by excluding characters.

    Args:
        pw_length (int): The number of characters the generated password
            should have.
        alphanumeric_characters_only (bool, optional): A flag to indicate
            whether to restrict character set to only letters and numbers.
            Defaults to False.
        excluded_characters (list, optional): A list of characters to exclude
            from character set. Defaults to empty list.

    Returns:
        str: randomly generated password following given constraints (length,
            character set)

    """
    # decide which character set to use
    if alphanumeric_characters_only:
        characters = alphanumeric_character_set
    else:
        characters = full_character_set

    # remove excluded characters from character set
    for char in excluded_characters:
        if len(char) == 1:
            characters.replace(char, "")

    password = "".join(random.choice(characters) for x in range(int(pw_length)))
    return password


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--length",
        metavar="int",
        type=int,
        default=16,
        help="length of password to generate (default: 16)",
    )
    parser.add_argument(
        "-a",
        "--alphanumeric-only",
        action="store_true",
        help="only use alphanumeric characters in password",
    )
    parser.add_argument(
        "-x",
        "--exclude",
        metavar="str",
        type=str,
        default="",
        help="string of characters to exclude from using in password",
    )
    args = parser.parse_args()

    print(generate_password(args.length, args.alphanumeric_only, list(args.exclude)))


if __name__ == "__main__":
    main()
