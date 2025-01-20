"""Backup books from macOS Books to usable ePubs."""

import subprocess

from termcolor import cprint

from bochord.epub_dir import backup_epub_dir

__version__ = "1.1.0"


def backup_file(filename, args):
    """Backup documents that aren't epub directories."""
    verbose = "-v" if args.verbose else "-q"
    subprocess.call(["rsync", "-aP", verbose, filename, args.dest])  # noqa: S603,S607


def prune(args):
    """Prune docs from destination that aren't in the source."""
    dest_set = set(args.dest.iterdir())
    src_set = set(args.source.iterdir())
    extra_set = dest_set - src_set
    if args.verbose:
        cprint(f"Removing: {extra_set}", "yellow")
    for filename in extra_set:
        filename.unlink()
        cprint("\tRemoved: {filename}", "yellow")


def run(args):
    """Backup everything."""
    for filename in args.source.iterdir():
        if filename.suffix == ".epub" and filename.is_dir():
            backup_epub_dir(filename, args)
        else:
            backup_file(filename, args)

    if args.prune:
        prune(args)
