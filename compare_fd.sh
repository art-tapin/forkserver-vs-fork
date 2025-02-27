#!/usr/bin/env bash

# compare_fd.sh with summary of FD usage
# --------------------------------------

make postgres  # Start or ensure Postgres is up (skip if you have your own DB)

function run_test() {
    CONFIG_FILE="$1"
    LABEL="$2"

    echo "=== Starting dispatcher with $CONFIG_FILE ($LABEL) ==="
    PYTHONPATH=$PWD dispatcher-standalone --config "$CONFIG_FILE" &
    DISP_PID=$!
    sleep 3  # wait for dispatcher to start

    # Submit tasks
    NUM_TASKS=50
    echo "Submitting $NUM_TASKS tasks to $LABEL..."
    PYTHONPATH=$PWD python submit_many_tasks.py "$CONFIG_FILE" "$NUM_TASKS"
    sleep 5  # Let tasks spin up workers

    # Capture FD usage lines in a tmp file
    TMPFILE=$(mktemp)
    python pid-host-to-container.py "dispatcher" > "$TMPFILE"
    
    # Build a pattern that matches the exact command line
    # e.g. "dispatcher-standalone.*config_fork.yml" or "dispatcher-standalone.*config_forkserver.yml"
    PATTERN='(dispatcher-standalone|ForkServerManager|python.*forkserver)'
    echo "Using regex pattern: $PATTERN"

    python pid-host-to-container.py "$PATTERN" > "$TMPFILE"

    echo "===$LABEL FD lines from pid-host-to-container.py ==="
    cat "$TMPFILE"

    # parse FD lines
    # lines look like: "Container PID: 201159, Open File Descriptors: 51"
    FD_VALUES=$(grep -oE 'Open File Descriptors: [0-9]+' "$TMPFILE" | awk '{print $4}')

    # compute min, max, average
    MIN_FD=$(echo "$FD_VALUES" | sort -n | head -1)
    MAX_FD=$(echo "$FD_VALUES" | sort -n | tail -1)
    AVG_FD=$(awk '{ sum += $1; count++ } END { if (count>0) print int(sum/count); else print 0 }' <<< "$FD_VALUES")

    echo "Summary ($LABEL):"
    echo "  - Workers matched: $(echo "$FD_VALUES" | wc -l)"
    echo "  - Min FD: $MIN_FD"
    echo "  - Max FD: $MAX_FD"
    echo "  - Avg FD: $AVG_FD"

    # Clean up
    rm -f "$TMPFILE"

    # Kill dispatcher
    kill $DISP_PID
    wait $DISP_PID 2>/dev/null || true
    echo "=== Dispatcher $LABEL stopped ==="
    echo "--------------------------------------------------"
}

# 1) Run test for 'fork'
run_test "config_fork.yml" "FORK"

# 2) Run test for 'forkserver'
run_test "config_forkserver.yml" "FORKSERVER"

echo "Tests complete. Compare FD usage from the summary lines above!"

