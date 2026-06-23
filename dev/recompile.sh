#!/bin/bash

# Parse flags: --local is consumed by the script, everything else passed to compiler
local_mode=false
compiler_flags=()
for arg in "$@"; do
    case $arg in
        --local) local_mode=true ;;
        *) compiler_flags+=("$arg") ;;
    esac
done
flags="${compiler_flags[*]}"

# Helper to run commands with or without pixi
run_cmd() {
    if [ "$local_mode" = true ]; then
        "$@"
    else
        pixi run --manifest-path pixi.toml -e compile "$@"
    fi
}

# Derive generated directory from spec.yaml id field
WORKFLOW_ID=$(grep '^id:' spec.yaml | sed 's/^id: *//' | tr '_' '-')
GENERATED_DIR="ecoscope-workflows-${WORKFLOW_ID}-workflow"

if [ "$local_mode" = false ]; then
    pixi update --manifest-path pixi.toml -e compile
fi

# (re)initialize dot executable to ensure graphviz is available
run_cmd dot -c

echo "recompiling spec.yaml with flags '--clobber ${flags}'"

run_cmd ecoscope-workflows compile --spec spec.yaml --clobber ${flags}
compile_exit=$?

exit $compile_exit