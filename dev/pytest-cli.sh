#!/bin/bash

set -e  # Exit on error

# Parse arguments
workflow_name=$1
shift  # Remove first argument to process remaining flags

skip_setup=false
local_mode=false
run_all=false
quiet=false
test_case=""

# Check for flags
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-setup)
            skip_setup=true
            shift
            ;;
        --local)
            local_mode=true
            skip_setup=true  # --local implies --skip-setup
            shift
            ;;
        --all)
            run_all=true
            shift
            ;;
        --quiet|-q)
            quiet=true
            shift
            ;;
        --case)
            test_case="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [ -z "$workflow_name" ]; then
    echo "Usage: $0 <workflow_name> <--all | --case test_case_name> [--skip-setup] [--local] [--quiet|-q]"
    echo "Examples:"
    echo "  $0 download-events --case with-attachments    # Run single test case"
    echo "  $0 download-events --all                       # Run all test cases"
    echo "  $0 download-events --all --quiet               # Minimal output"
    echo "Options:"
    echo "  --case <name>   Run a specific test case"
    echo "  --all           Run all test cases for the workflow"
    echo "  --skip-setup    Skip pixi update and playwright-install steps"
    echo "  --local         Run commands directly without pixi (implies --skip-setup)"
    echo "  --quiet, -q     Minimal output: only show pass/fail and errors"
    exit 1
fi

if [ "$run_all" = false ] && [ -z "$test_case" ]; then
    echo "ERROR: Must specify either --all or --case <test_case_name>"
    exit 1
fi

if [ "$run_all" = true ] && [ -n "$test_case" ]; then
    echo "ERROR: Cannot specify both --all and --case"
    exit 1
fi

workflow_dash=$(echo $workflow_name | tr '_' '-')

# Get absolute paths
repo_root=$(pwd)
workflow_dir="${repo_root}/ecoscope-workflows-${workflow_dash}-workflow"
manifest_path="${workflow_dir}/pixi.toml"
test_cases_file="${repo_root}/test-cases.yaml"

if [ "$quiet" = false ]; then
    echo "=========================================="
    echo "Workflow: $workflow_name"
    if [ "$run_all" = true ]; then
        echo "Running: ALL test cases"
    else
        echo "Test case: $test_case"
    fi
    echo "Mode: $([ "$local_mode" = true ] && echo "local" || echo "pixi")"
    echo "=========================================="
fi

# Helper function to run commands with or without pixi
run_cmd() {
    if [ "$local_mode" = true ]; then
        # Run command directly
        eval "$@"
    else
        # Run command with pixi
        pixi run --manifest-path $manifest_path --locked -e default "$@"
    fi
}

# Optional setup steps
if [ "$skip_setup" = false ]; then
    [ "$quiet" = false ] && echo "Updating pixi environment..."
    pixi update --manifest-path $manifest_path
    [ "$quiet" = false ] && echo "Installing playwright..."
    run_cmd pip install playwright
    run_cmd bash -c "playwright install --with-deps chromium"
else
    [ "$quiet" = false ] && echo "Skipping pixi update and playwright-install (--skip-setup or --local flag provided)"
fi

# Function to run a single test case
run_single_test_case() {
    local test_case=$1

    if [ "$quiet" = false ]; then
        echo ""
        echo "=========================================="
        echo "Running test case: $test_case"
        echo "=========================================="
    fi

    # Verify test case exists
    if ! yq -e ".\"${test_case}\"" "$test_cases_file" > /dev/null 2>&1; then
        echo "✗ $test_case — ERROR: test case not found in $test_cases_file"
        return 1
    fi

    # Extract mock_io setting from test case (defaults to true if not specified)
    if yq -e ".\"${test_case}\" | has(\"mock_io\")" "$test_cases_file" > /dev/null 2>&1; then
        use_mock_io=$(yq ".\"${test_case}\".mock_io" "$test_cases_file")
    else
        use_mock_io="true"
    fi
    [ "$quiet" = false ] && echo "Mock IO mode: $use_mock_io"

    # Create temporary results directory (cross-platform compatible)
    # Use RUNNER_TEMP if available (GitHub Actions), otherwise fall back to /tmp
    temp_base="${RUNNER_TEMP:-/tmp}"
    results_dir="${temp_base}/workflow-test-results/${workflow_name}/${test_case}"
    rm -rf "$results_dir"
    mkdir -p "$results_dir"
    [ "$quiet" = false ] && echo "Created results directory: $results_dir"
    [ "$quiet" = false ] && echo ""

    # Export ECOSCOPE_WORKFLOWS_RESULTS for workflow to use
    export ECOSCOPE_WORKFLOWS_RESULTS="file://${results_dir}"

    # Extract params for this test case
    params_file="${results_dir}/params.yaml"
    yq ".\"${test_case}\".params" "$test_cases_file" > "$params_file"

    if [ "$quiet" = false ]; then
        echo "Extracted params:"
        cat "$params_file"
        echo ""
    fi

    # Run workflow CLI directly
    if [ "$quiet" = false ]; then
        echo "Executing workflow..."
        echo "Results will be written to: $ECOSCOPE_WORKFLOWS_RESULTS"
        echo ""
    fi

    cd "$workflow_dir"
    workflow_underscore=$(echo $workflow_name | tr '-' '_')

    # Build the command with conditional --mock-io flag
    cmd="python -m ecoscope_workflows_${workflow_underscore}_workflow.cli run --config-file $params_file --execution-mode sequential"
    if [ "$use_mock_io" = "true" ]; then
        cmd="$cmd --mock-io"
    fi

    if [ "$quiet" = false ]; then
        echo "Command: $cmd"
        echo ""
    fi

    # Run the command and capture exit code
    if [ "$quiet" = true ]; then
        if run_cmd $cmd > /dev/null 2>&1; then
            cmd_exit_code=0
        else
            cmd_exit_code=$?
        fi
    else
        if run_cmd $cmd; then
            cmd_exit_code=0
        else
            cmd_exit_code=$?
        fi
    fi

    # Return to repo root
    cd "$repo_root"

    # Validate result.json
    result_json="${results_dir}/result.json"
    if [ ! -f "$result_json" ]; then
        echo "✗ $test_case — result.json not found at $result_json"
        return 1
    fi

    [ "$quiet" = false ] && echo ""
    [ "$quiet" = false ] && echo "Validating result.json..."
    error_value=$(jq -r '.error // "null"' "$result_json")

    if [ "$error_value" != "null" ] || [ $cmd_exit_code -ne 0 ]; then
        echo "✗ $test_case — FAILED"
        if [ "$error_value" != "null" ]; then
            echo "  Error: $(jq -r '.error' "$result_json")"
        fi
        [ "$quiet" = false ] && echo "" && echo "Full result.json:" && cat "$result_json"
        return 1
    fi

    echo "✓ $test_case — passed"
    if [ "$quiet" = false ]; then
        echo ""
        echo "Full result.json:"
        cat "$result_json"
    fi

    return 0
}

# Main logic: run all test cases or a single one
if [ "$run_all" = true ]; then
    # Get all test case names from test-cases.yaml
    # tr -d '\r' removes carriage returns for Windows compatibility
    test_cases=($(yq 'keys | .[]' "$test_cases_file" | tr -d '"\r'))

    if [ "$quiet" = false ]; then
        echo ""
        echo "Found ${#test_cases[@]} test cases: ${test_cases[*]}"
        echo ""
    fi

    # Track results
    declare -a failed_cases
    declare -a passed_cases

    # Loop through each test case
    for test_case in "${test_cases[@]}"; do
        if run_single_test_case "$test_case"; then
            passed_cases+=("$test_case")
        else
            failed_cases+=("$test_case")
            # Continue to next test case instead of exiting (don't let set -e stop us)
            true
        fi
    done

    # Print summary
    echo ""
    echo "=========================================="
    echo "TEST SUMMARY"
    echo "=========================================="
    echo "Total: ${#test_cases[@]}"
    echo "Passed: ${#passed_cases[@]}"
    echo "Failed: ${#failed_cases[@]}"
    echo ""

    if [ ${#passed_cases[@]} -gt 0 ]; then
        echo "✓ Passed test cases:"
        for case in "${passed_cases[@]}"; do
            echo "  - $case"
        done
        echo ""
    fi

    if [ ${#failed_cases[@]} -gt 0 ]; then
        echo "✗ Failed test cases:"
        for case in "${failed_cases[@]}"; do
            echo "  - $case"
        done
        echo ""
        exit 1
    fi

    echo "✓ All tests passed!"

else
    # Run single test case
    run_single_test_case "$test_case"
fi