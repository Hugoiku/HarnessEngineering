#!/usr/bin/env bash
set -euo pipefail
FILE="${1:?file path}"
[[ -f "$FILE" ]]
