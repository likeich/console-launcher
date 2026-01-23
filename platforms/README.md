# Platform Configuration Data

This directory contains platform configuration files for Console Launcher.

## Structure

- **index.json**: Master index of all available platforms with revision tracking
- **Individual platform files**: JSON files defining emulator cores, file extensions, and metadata for each gaming platform

## Source

Platform data is synced from [magneticchen/Daijishou](https://github.com/magneticchen/Daijishou) via GitHub Actions workflow.

Test files (*.test), deprecated files (*.deprecated), and Python scripts (*.py) are automatically excluded during sync.

## Usage

Console Launcher Native fetches platform data from:
```
https://raw.githubusercontent.com/likeich/console-launcher/main/platforms/index.json
```

Users can customize this URL in **Settings > Frontend > Platform Settings**.
