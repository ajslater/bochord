"""Backup iCloud iBooks epub dir as an epub archive."""
# iCloud stores epubs exploded on disk.

import os
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from termcolor import cprint

ZIP_MTIME_MIN = 315644400.0  # 1 day after 1980 for timezones


def _get_src_file_mtime(src_file_path: Path):
    """Get source file mtime, but alter it if pkzip will reject it."""
    src_file_mtime = src_file_path.stat().st_mtime
    if src_file_mtime < ZIP_MTIME_MIN:
        cprint(f"\tUpdating mtime for zip compatibility: {src_file_path}", "yellow")
        src_file_path.touch()
        src_file_mtime = src_file_path.stat().st_mtime
    return src_file_mtime


def get_dest_file_mtime(filename: Path, args):
    """Get Destination file mtime."""
    dest_path = args.dest / filename.name
    return dest_path.stat().st_mtime if dest_path.exists() else 0.0


def _get_updated_files(archive_mtime: float, src_dir: Path, args):
    """Check for updated files."""
    src_paths = set()
    update = False

    for root, _, src_files in os.walk(src_dir):
        root_path = Path(root)
        for src_filename in sorted(src_files):
            src_file_path = root_path / src_filename
            src_paths.add(src_file_path)
            src_file_mtime = _get_src_file_mtime(src_file_path)
            update = update or src_file_mtime > archive_mtime

    if not update and not args.force:
        src_paths = set()

    return src_paths


def _archive_epub(epub_path, src_paths, args):
    """Make a new archive in a tempfile."""
    cprint(f"\nArchiving: {epub_path.name}", "cyan")
    new_epub_path = epub_path.with_suffix(".epub_new")

    with ZipFile(
        new_epub_path, mode="w", compression=ZIP_DEFLATED, compresslevel=9
    ) as epub:
        for src_file_path in src_paths:
            ctype = ZIP_STORED if src_file_path.name == "mimetype" else ZIP_DEFLATED
            if args.verbose:
                cprint(f"\t{src_file_path}", "cyan")
            epub.write(src_file_path, compress_type=ctype)

    # Move tempfile over old epub
    new_epub_path.rename(epub_path)


def backup_epub_dir(epub_dir_path, args):
    """Compress the exploded epub dir to the backup destination."""
    dest_path = args.dest / epub_dir_path.name
    archive_mtime = get_dest_file_mtime(epub_dir_path, args)
    if src_paths := _get_updated_files(archive_mtime, epub_dir_path, args):
        _archive_epub(dest_path, src_paths, args)
        return True
    return False
