#!/usr/bin/env bash
# Install once: copy folder action script and attach to Dropbox VIDEO. Idempotent.

set -e
REPO="$HOME/Sites/retroverse"
SCRIPT_NAME="retroverse_faststart.scpt"
DEST_DIR="$HOME/Library/Scripts/Folder Action Scripts"
DEST="$DEST_DIR/$SCRIPT_NAME"
VIDEO_DIR="$HOME/Library/CloudStorage/Dropbox/VIDEO"
FOLDER_ACTION_NAME="RetroVerse VIDEO"

# Compile and copy script
mkdir -p "$DEST_DIR"
osacompile -o "$DEST" "$REPO/tools/media-normalization/folder-action.scpt"

# Enable Folder Actions
defaults write com.apple.FolderActionsDispatcher folderActionsEnabled -bool true 2>/dev/null || true

# Remove existing attachment by name so re-run is safe
osascript -e "
tell application \"System Events\"
	try
		delete folder action \"$FOLDER_ACTION_NAME\"
	end try
end tell
" 2>/dev/null || true

# Attach script to VIDEO folder (path as alias from POSIX)
osascript -e "
set videoPath to \"$VIDEO_DIR\"
set folderAlias to (POSIX file videoPath) as alias
tell application \"System Events\"
	make new folder action at end of folder actions with properties {enabled:true, name:\"$FOLDER_ACTION_NAME\", path:folderAlias}
	tell folder action \"$FOLDER_ACTION_NAME\" to make new script at end of scripts with properties {name:\"$SCRIPT_NAME\"}
end tell
"

echo "Folder action installed: $SCRIPT_NAME attached to $VIDEO_DIR"
