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

# Package name and results variable as the committed package (and the other workflow repos) use;
# wt-compiler's defaults would emit wt-animate-tracks-workflow/ reading WT_RESULTS instead.
run_cmd wt-compiler compile --spec spec.yaml \
    --pkg-name-prefix=ecoscope-workflows \
    --results-env-var=ECOSCOPE_WORKFLOWS_RESULTS \
    --clobber ${flags}
compile_exit=$?

exit $compile_exit