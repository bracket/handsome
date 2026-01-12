#!/usr/bin/env bash
# Script to install git hooks

HOOK_DIR=".git/hooks"
SOURCE_DIR="hooks"

if [ ! -d "$HOOK_DIR" ]; then
    echo "Error: Not in a git repository"
    exit 1
fi

if [ ! -f "$SOURCE_DIR/pre-commit" ]; then
    echo "Error: Source pre-commit hook not found at $SOURCE_DIR/pre-commit"
    exit 1
fi

# Install pre-commit hook
cp "$SOURCE_DIR/pre-commit" "$HOOK_DIR/pre-commit"
chmod +x "$HOOK_DIR/pre-commit"

echo "Git hooks installed successfully!"
