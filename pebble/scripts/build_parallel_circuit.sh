#!/usr/bin/env bash
set -euo pipefail

deck_dir="$(cd "$(dirname "$0")/.." && pwd)"
build_dir="$deck_dir/.generated/parallel-circuit"
asset_dir="$deck_dir/public/figures"
mkdir -p "$build_dir" "$asset_dir"

pdflatex -halt-on-error -interaction=nonstopmode -output-directory="$build_dir" \
  "$deck_dir/scripts/parallel_computation.tex" > "$build_dir/build.log"
pdftocairo -svg "$build_dir/parallel_computation.pdf" "$asset_dir/parallel-computation.svg"
pdftocairo -png -singlefile -r 200 "$build_dir/parallel_computation.pdf" "$asset_dir/parallel-computation"
