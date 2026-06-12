# Usage Examples

Real commands for common file-organizer workflows.

## Preview before committing
Always start with a dry run so nothing moves until you're sure:

    file-organizer ./Downloads --dry-run

## Organize a single folder
    file-organizer ./Downloads

## Recurse into subfolders
    file-organizer ./Projects --recursive

## Only touch large files
Useful when clearing space - skip anything under 50 MB:

    file-organizer ./Downloads --min-size 50MB

## Use a custom category config
    file-organizer ./Downloads --config ./my-categories.yaml

## Undo the last run
If a run grouped things in a way you didn't want:

    file-organizer --undo

## Generate a summary chart
    file-organizer ./Downloads --summary
