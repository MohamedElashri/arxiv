#!/usr/bin/env bash
set -euo pipefail

version=0.8.5
checksum=a982311b61210a0e30be5408453e3176d9decbabce6612e61c01433266f3f70f
archive="nida_${version}_linux_x86_64.tar.gz"
bin_dir="$RUNNER_TEMP/nida-bin"

curl --fail --silent --show-error --location --retry 3 \
  "https://github.com/MohamedElashri/nida/releases/download/v${version}/$archive" \
  --output "$RUNNER_TEMP/$archive"
printf '%s  %s\n' "$checksum" "$RUNNER_TEMP/$archive" | sha256sum --check --strict
mkdir -p "$bin_dir"
tar -xzf "$RUNNER_TEMP/$archive" -C "$bin_dir" nida
printf '%s\n' "$bin_dir" >> "$GITHUB_PATH"
