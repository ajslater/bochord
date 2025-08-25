"""Backup books from macOS Books to usable ePubs."""

import shutil
from argparse import Namespace
from pathlib import Path

from termcolor import cprint

from bochord.epub_dir import backup_epub_dir, get_dest_file_mtime


def backup_file(filename: Path, args: Namespace) -> bool:
    """Backup documents that aren't epub directories."""
    src_path = args.source / filename.name
    src_file_mtime = src_path.stat().st_mtime
    dest_path = args.dest / filename.name
    dest_file_mtime = get_dest_file_mtime(dest_path)
    if args.force or src_file_mtime > dest_file_mtime:
        cprint(f"\nArchiving: {filename}", "cyan")
        shutil.copy2(src_path, dest_path)
        return True
    return False


def prune(args: Namespace) -> None:
    """Prune docs from destination that aren't in the source."""
    dest_set = set(args.dest.iterdir())
    src_set = set(args.source.iterdir())
    extra_set = sorted(dest_set - src_set)
    if args.verbose:
        cprint(f"Removing: {extra_set}", "yellow")
    for filename in extra_set:
        filename.unlink()
        cprint("\tRemoved: {filename}", "yellow")


def read_source_dir(source: Path):
    """List source dir that may not be ready yet."""
    try:
        filenames = sorted(source.iterdir())
    except InterruptedError as exc:
        cprint(exc)
        cprint(
            f"You probably need to allow this python script permission to access {source}. There's likely a pop up dialog requesting this.",
            "yellow",
        )
        raise
    except:
        raise
    return filenames


def run(args: Namespace) -> None:
    """Backup everything."""
    filenames = read_source_dir(args.source)
    for filename in filenames:
        backup_func = (
            backup_epub_dir
            if filename.suffix == ".epub" and filename.is_dir()
            else backup_file
        )
        if not backup_func(filename, args):
            if args.verbose:
                cprint(f"\nNot updated: {filename}", "green")
            else:
                cprint(".", "green", end="")

    if not args.verbose:
        cprint("")

    if args.prune:
        prune(args)
