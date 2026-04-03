#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <tex-file>" >&2
  exit 1
fi

input_path="$1"

if [[ ! -f "$input_path" ]]; then
  echo "file not found: $input_path" >&2
  exit 1
fi

resolve_path() {
  local path="$1"
  local dir
  dir="$(cd "$(dirname "$path")" && pwd)"
  printf '%s/%s\n' "$dir" "$(basename "$path")"
}

detect_engine() {
  local tex_file="$1"
  local engine

  engine="$(
    sed -n '1,20p' "$tex_file" \
      | sed -nE 's/^%[[:space:]]*!TEX[[:space:]]+program[[:space:]]*=[[:space:]]*([[:alnum:]-]+)[[:space:]]*$/\1/p' \
      | tail -n 1
  )"

  if [[ -z "$engine" ]]; then
    engine="xelatex"
  fi

  printf '%s\n' "$engine"
}

find_main_tex() {
  local current_dir="$1"

  while [[ "$current_dir" != "/" ]]; do
    if [[ -f "$current_dir/main.tex" ]]; then
      printf '%s/main.tex\n' "$current_dir"
      return 0
    fi
    current_dir="$(dirname "$current_dir")"
  done

  return 1
}

cleanup_root_artifacts() {
  local base="$1"

  rm -f \
    "$base.aux" \
    "$base.bbl" \
    "$base.bcf" \
    "$base.blg" \
    "$base.fdb_latexmk" \
    "$base.fls" \
    "$base.lof" \
    "$base.log" \
    "$base.lot" \
    "$base.nav" \
    "$base.out" \
    "$base.run.xml" \
    "$base.snm" \
    "$base.synctex.gz" \
    "$base.toc" \
    "$base.vrb" \
    "$base.xdv"
}

tex_file="$(resolve_path "$input_path")"
tex_dir="$(dirname "$tex_file")"

if [[ "$(basename "$tex_file")" == "main.tex" ]]; then
  root_tex="$tex_file"
else
  root_tex="$(find_main_tex "$tex_dir" || true)"
  if [[ -z "$root_tex" ]]; then
    root_tex="$tex_file"
  fi
fi

root_dir="$(dirname "$root_tex")"
root_name="$(basename "$root_tex")"
root_base="${root_name%.tex}"
out_dir="$root_dir/builds"
aux_file="$out_dir/$root_base.aux"
build_pdf="$out_dir/$root_base.pdf"
final_pdf="$root_dir/$root_base.pdf"
engine="$(detect_engine "$root_tex")"

mkdir -p "$out_dir"
cd "$root_dir"
cleanup_root_artifacts "$root_base"

if ! command -v "$engine" >/dev/null 2>&1; then
  echo "LaTeX engine not found: $engine" >&2
  exit 1
fi

"$engine" -synctex=1 -interaction=nonstopmode -file-line-error -output-directory="$out_dir" "$root_name"

if [[ -f "$aux_file" ]] && grep -q '^\\bibdata{' "$aux_file" && grep -q '^\\citation{' "$aux_file"; then
  (
    cd "$root_dir"
    bibtex "builds/$root_base"
  )
fi

"$engine" -synctex=1 -interaction=nonstopmode -file-line-error -output-directory="$out_dir" "$root_name"
"$engine" -synctex=1 -interaction=nonstopmode -file-line-error -output-directory="$out_dir" "$root_name"

if [[ -f "$build_pdf" ]]; then
  cp "$build_pdf" "$final_pdf"
fi

cleanup_root_artifacts "$root_base"
