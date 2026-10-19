#!/usr/bin/env bash
# One wave = two models, one per card, same suite. Usage:
#   run_wave.sh NAME FILE DEV PORT NAME FILE DEV PORT [SAMPLES]
set -u

BIN=$HOME/llama.cpp/build-mixed/bin/llama-server
MB=/home/hati/code/modelbench/.venv/bin/modelbench
OUT=/home/hati/.hermes/cache/scratch/smallbench
mkdir -p "$OUT/runs"

SAMPLES=${9:-2}
T=4

run_one() {
    local name=$1 model=$2 dev=$3 port=$4
    "$BIN" -m "$model" -a "$name" -c 16384 -np 1 -ngl all -fa on --jinja \
        -sm none -dev "$dev" -t "$T" -tb "$T" -b 2048 -ub 512 -n 8192 \
        -ctk q8_0 -ctv q8_0 \
        --host 127.0.0.1 --port "$port" > "$OUT/$name.server.log" 2>&1 &
    local pid=$!
    local ok=0
    for _ in $(seq 1 180); do
        if curl -s --noproxy '*' -m 2 "http://127.0.0.1:$port/health" | grep -q '"ok"'; then ok=1; break; fi
        sleep 2
    done
    if [[ $ok -ne 1 ]]; then
        echo "$name: server never came up" >> "$OUT/progress.log"
        kill "$pid" 2>/dev/null
        return
    fi
    echo "$name: up on $port ($dev) $(date +%H:%M:%S)" >> "$OUT/progress.log"
    "$MB" run --base-url "http://127.0.0.1:$port/v1" --model "$name" --name "$name" \
        --suite core-v2 --out "$OUT/runs/$name" --jobs 1 --samples "$SAMPLES" \
        > "$OUT/$name.run.log" 2>&1
    echo "$name: exit=$? $(date -Is)" >> "$OUT/progress.log"
    kill "$pid" 2>/dev/null
    wait "$pid" 2>/dev/null
}

run_one "$1" "$2" "$3" "$4" &
run_one "$5" "$6" "$7" "$8" &
wait
echo "WAVE DONE $1 $5 $(date -Is)" >> "$OUT/progress.log"
