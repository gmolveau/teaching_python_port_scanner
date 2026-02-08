"""
exemple de l'utilisation de argparse pour faire un cli avec plusieurs sous-commandes

ici un cli qui tente de reproduire les commandes git clone, et git commit
"""

import argparse


def cli():
    parser = argparse.ArgumentParser(description="a git cli example")
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument(
        "-v",
        "--verbose",
        help="Common top-level parameter",
        action="store_true",
        required=False,
    )
    subparsers = parser.add_subparsers(dest="command")
    # clone command
    clone_parser = subparsers.add_parser(
        "clone", description="clone command", help="clone a repo", parents=[base_parser]
    )
    clone_parser.add_argument("url", help="repo url")
    # commit command
    commit_parser = subparsers.add_parser(
        "commit",
        description="commit command",
        help="commit files",
        parents=[base_parser],
    )
    commit_parser.add_argument("-m", help="commit message")
    args = parser.parse_args()
    return args


def main():
    args = cli()
    print(args)
    print(f"la commande lancée est {args.command}")


if __name__ == "__main__":
    main()
