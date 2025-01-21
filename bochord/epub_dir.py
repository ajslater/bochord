"""Backup iCloud iBooks epub dir as an epub archive."""
# iCloud stores epubs exploded on disk.

import os
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile

from termcolor import cprint

ZIP_MTIME_MIN = 315644400.0  # 1 day after 1980 for timezones


def _get_src_file_mtime(src_file_path):
    """Get source file mtime, but alter it if pkzip will reject it."""
    src_file_mtime = src_file_path.stat().st_mtime
    if src_file_mtime < ZIP_MTIME_MIN:
        cprint(f"Updating mtime for zip compatibility: {src_file_path}", "yellow")
        src_file_path.touch()
        src_file_mtime = src_file_path.stat().st_mtime
    return src_file_mtime


def _check_for_updated_files(epub_path, src_dir, args):
    """Check for updated files."""
    archive_mtime = epub_path.stat().st_mtime if Path(epub_path).exists() else 0.0

    src_paths = set()
    update = False

    for root, _, src_files in os.walk(src_dir):
        rp = Path(root)
        for src_filename in src_files:
            src_file_path = rp / src_filename
            src_paths.add(src_file_path)
            src_file_mtime = _get_src_file_mtime(src_file_path)
            update = update or src_file_mtime > archive_mtime

    if not update and not args.force:
        src_paths = False

    return src_paths


def _archive_epub(epub_path, src_paths, args):
    """Make a new archive in a tempfile."""
    cprint(f"Archiving: {epub_path.name}", "cyan")
    new_epub_path = epub_path.with_suffix(".epub_new")

    with ZipFile(new_epub_path, "w") as epub:
        for src_file_path in src_paths:
            ctype = ZIP_STORED if src_file_path.name == "mimetype" else None
            if args.verbose:
                cprint(f"\t{src_file_path}", "cyan")
            epub.write(src_file_path, compress_type=ctype, compresslevel=9)

    # Move tempfile over old epub
    new_epub_path.rename(epub_path)


def backup_epub_dir(filename, args):
    """Compress the exploded epub dir to the backup destination."""
    epub_path = args.dest / filename.name

    src_paths = _check_for_updated_files(epub_path, filename, args)

    if not src_paths:
        if args.verbose:
            cprint(f"Epub contents not updated, skipping: {epub_path}", "green")
        else:
            cprint(".", "green", end="")
        return

    _archive_epub(epub_path, src_paths, args)
