# bochord

Backup books from macOS Books to usable ePubs

This works because macOS Books with iCloud turned on stores books as exploded
epub directories with their proper titles as the directory name. This program
zips them up to a specified backup dir and copies PDFs with rsync to that dir as
well.

## Depends

Depends on rsync being installed and on the path.

## Why

I like to manage my books with Apple Books instead of Calibre for convenience on
all my Apple devices, but Apple makes it a pain to export books programatically.
Backing up books like this also defends against Apple making all my books
inaccessable someday for no reason.
