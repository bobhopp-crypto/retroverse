# Media normalization (folder action)

Runs **fast-start MP4 normalization** on files added to a folder: when a file is added, the folder action calls `tools/faststart_mp4.sh` with its full path so the file is rewritten with `movflags +faststart` for web-friendly playback.

- **Why the script lives in Library:** macOS only runs folder action scripts from `~/Library/Scripts/Folder Action Scripts/`. The installer compiles the source from this repo and copies the compiled `.scpt` there. That copy is a thin stub; the **source of truth** stays in RetroVerse (`tools/media-normalization/folder-action.scpt` and `tools/faststart_mp4.sh`).

**Install once:** from the repo root, run:

```bash
./tools/media-normalization/install-folder-action.sh
```

This compiles and copies the script, enables Folder Actions if needed, and attaches the action to `~/Library/CloudStorage/Dropbox/VIDEO`. Safe to run multiple times.
