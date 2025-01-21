"""Backup books from macOS Books to usable ePubs."""

import subprocess
from pathlib import Path

from termcolor import cprint

from bochord.epub_dir import backup_epub_dir, get_dest_file_mtime

__version__ = "1.1.0"


def backup_file(filename: Path, args):
    """Backup documents that aren't epub directories."""
    src_path = args.source / filename.name
    src_file_mtime = src_path.stat().st_mtime
    dest_file_mtime = get_dest_file_mtime(filename, args)
    if args.force or src_file_mtime > dest_file_mtime:
        cprint(f"\nArchiving: {filename}", "cyan")
        verbose = "-v" if args.verbose else "-q"
        subprocess_args = ("rsync", "-aP", verbose, str(src_path), args.dest)
        subprocess.call(subprocess_args)  # noqa: S603
        return True
    return False


def prune(args):
    """Prune docs from destination that aren't in the source."""
    dest_set = set(args.dest.iterdir())
    src_set = set(args.source.iterdir())
    extra_set = sorted(dest_set - src_set)
    if args.verbose:
        cprint(f"Removing: {extra_set}", "yellow")
    for filename in extra_set:
        filename.unlink()
        cprint("\tRemoved: {filename}", "yellow")


def run(args):
    """Backup everything."""
    for filename in sorted(args.source.iterdir()):
        if filename.suffix == ".epub" and filename.is_dir():
            result = backup_epub_dir(filename, args)
        else:
            result = backup_file(filename, args)

        if not result:
            if args.verbose:
                cprint(f"\nNot updated: {filename}", "green")
            else:
                cprint(".", "green", end="")

    if not args.verbose:
        cprint("")

    if args.prune:
        prune(args)
