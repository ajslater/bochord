#!/usr/bin/env python3
"""Backup books from macOS Books to usable ePubs"""

import argparse

import os
import subprocess
import zipfile
from pathlib import Path

__version__ = "1.0.0"
ICLOUD_BOOK_DIR = "Library/Mobile Documents/iCloud~com~apple~iBooks/Documents"
ZIP_MTIME_MIN = 315644400.0  # 1 day after 1980 for timezones


def get_src_file_mtime(src_file_path):
    """Get source file mtime, but alter it if pkzip will reject it."""
    src_file_mtime = src_file_path.stat().st_mtime
    if src_file_mtime < ZIP_MTIME_MIN:
        print("Updating mtime for zip compatibilty:", src_file_path)
        src_file_path.touch()
        src_file_mtime = src_file_path.stat().st_mtime
    return src_file_mtime


def check_for_updated_files(epub_path, src_dir, args):
    """Check for updated files"""
    if Path(epub_path).exists():
        archive_mtime = epub_path.stat().st_mtime
    else:
        archive_mtime = 0.0

    src_paths = set()
    update = False

    for root, _, src_files in os.walk(src_dir):
        rp = Path(root)
        for src_filename in src_files:
            src_file_path = rp / src_filename
            src_paths.add(src_file_path)
            src_file_mtime = get_src_file_mtime(src_file_path)
            update = update or src_file_mtime > archive_mtime

    if not update and not args.force:
        src_paths = False

    return src_paths


def archive_epub(epub_path, src_paths, args):
    """Make a new archive in a tempfile."""
    print("Archiving:", epub_path.name)
    new_epub_path = epub_path + ".new"

    with zipfile.ZipFile(new_epub_path, "w") as epub:
        for src_file_path in src_paths:
            if src_file_path.name == "mimetype":
                ctype = zipfile.ZIP_STORED
            else:
                ctype = None
            if args.verbose:
                print("  ", src_file_path)
            epub.write(src_file_path, compress_type=ctype, compresslevel=9)

    # Move tempfile over old epub
    new_epub_path.rename(epub_path)


def backup_epub_dir(filename, args):
    """Compress the exploded epub dir to the backup destination."""
    epub_path = args.dest / filename.name

    src_paths = check_for_updated_files(epub_path, filename, args)

    if not src_paths:
        if args.verbose:
            print("Skipping:", epub_path)
        return

    archive_epub(epub_path, src_paths, args)


def backup_other(filename, args):
    """Backup documents that aren't epub directories."""
    if args.verbose:
        verbose = "-v"
    else:
        verbose = "-q"
    subprocess.call(["rsync", "-aP", verbose, filename, args.dest])


def prune(filenames, args):
    """Prune docs from destination that aren't in the source."""
    dest_set = set(args.dest.iterdir())
    src_set = set(filenames)
    extra_set = dest_set - src_set
    if args.verbose:
        print("Removing:")
        print(extra_set)
    for filename in extra_set:
        filename.unlink
        print("Removed:", filename)


def get_arguments():
    usage = "%(prog)s [options] <backup_path>"
    desc = "Backup books from macOS Books to usable ePubs"
    source = Path.home() / ICLOUD_BOOK_DIR
    parser = argparse.ArgumentParser(usage=usage, description=desc)
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        dest="force",
        default=0,
        help="force re-archive even if no file updates",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        default=0,
        help="be verbose",
    )
    parser.add_argument(
        "-p",
        "--prune",
        action="store_true",
        dest="prune",
        default=0,
        help="prune documents from destination if " "missing from source.",
    )
    parser.add_argument(
        "-s",
        "--source",
        action="store",
        dest="source",
        default=source,
        help="source directory (default: %(default)s)",
    )
    parser.add_argument(
        "dest", metavar="backup_path", type=Path, help="backup destination path"
    )

    return parser.parse_args()


def main(args):
    """Backup everything."""
    for filename in args.source.iterdir():
        if filename.suffix == ".epub" and filename.is_dir():
            backup_epub_dir(filename, args)
        else:
            backup_other(filename, args)

    if args.prune:
        prune(filenames, args)


if __name__ == "__main__":
    args = get_arguments()
    main(args)
