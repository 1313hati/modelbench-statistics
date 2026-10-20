#!/usr/bin/env bash
# Fresh-releases bench (Oct 2026): LFM2.5 trio, Prism ML ternary pair, and the
# LFM2.5 24B MoE across both cards. Same suite and flags as the 12 GB panel.
#
#   wave 1  lfm25-8b-a1b  CUDA0   lfm25-2.6b    CUDA1
#   wave 2  lfm25-1.2b    CUDA0   bonsai2-9b    CUDA1
#   wave 3  bonsai2-4b    CUDA0   (alone, 2-bit, short)
#   wave 4  lfm25-24b-a2b both cards (does not fit one 12 GB card)
set -u

MODELS=$HOME/.cache/llama-models
OUT=$HOME/.hermes/cache/scratch/freshbench
LOG=$OUT/progress.log
BIN=$HOME/llama.cpp/build-mixed/bin/llama-server
MB=/home/hati/code/modelbench/.venv/bin/modelbench
mkdir -p "$OUT/runs"

T=4
COMMON=(-c 16384 -np 1 -ngl all -fa on --jinja -t "$T" -tb "$T" -b 2048 -ub 512 -n 8192 -ctk q8_0 -ctv q8_0)

serve() {  # name file port devlist splitmode
    local name=$1 file=$2 port=$3 devs=$4 sm=$5
    if [[ ! -f "$MODELS/$file" ]]; then
        echo "$name: missing $file" >> "$LOG"; return 1
    fi
    "$BIN" -m "$MODELS/$file" -a "$name" "${COMMON[@]}" \
        -sm "$sm" -dev "$devs" --host 127.0.0.1 --port "$port" \
        > "$OUT/$name.server.log" 2>&1 &
    echo $!
}

wait_up() {  # port name
    local port=$1 name=$2
    for _ in $(seq 1 240); do
        if curl -s --noproxy '*' -m 2 "http://127.0.0.1:$port/health" | grep -q '"ok"'; then
            echo "$name: up on $port $(date +%H:%M:%S)" >> "$LOG"; return 0
        fi
        sleep 2
    done
    echo "$name: server never came up" >> "$LOG"; return 1
}

bench_one() {  # name port pid
    local name=$1 port=$2 pid=$3
    "$MB" run --base-url "http://127.0.0.1:$port/v1" --model "$name" --name "$name" \
        --suite core-v2 --out "$OUT/runs/$name" --jobs 1 --samples 1 \
        > "$OUT/$name.run.log" 2>&1
    echo "$name: exit=$? $(date -Is)" >> "$LOG"
    kill "$pid" 2>/dev/null
    wait "$pid" 2>/dev/null
}

pair() {  # n1 f1 p1 n2 f2 p2
    local n1=$1 f1=$2 p1=$3 n2=$4 f2=$5 p2=$6
    local a b
    a=$(serve "$n1" "$f1" "$p1" CUDA0 none) || return 1
    b=$(serve "$n2" "$f2" "$p2" CUDA1 none) || return 1
    wait_up "$p1" "$n1" || { kill "$a" "$b" 2>/dev/null; return 1; }
    wait_up "$p2" "$n2" || { kill "$a" "$b" 2>/dev/null; return 1; }
    bench_one "$n1" "$p1" "$a" &
    bench_one "$n2" "$p2" "$b" &
    wait
    echo "WAVE DONE $n1 $n2 $(date -Is)" >> "$LOG"
}

solo() {  # n1 f1 p1
    local n1=$1 f1=$2 p1=$3 a
    a=$(serve "$n1" "$f1" "$p1" CUDA0 none) || return 1
    wait_up "$p1" "$n1" || { kill "$a" 2>/dev/null; return 1; }
    bench_one "$n1" "$p1" "$a"
    echo "WAVE DONE $n1 - $(date -Is)" >> "$LOG"
}

dual() {  # n1 f1 p1   (both cards, one model)
    local n1=$1 f1=$2 p1=$3 a
    a=$(serve "$n1" "$f1" "$p1" CUDA0,CUDA1 row) || return 1
    wait_up "$p1" "$n1" || { kill "$a" 2>/dev/null; return 1; }
    bench_one "$n1" "$p1" "$a"
    echo "WAVE DONE $n1 dual $(date -Is)" >> "$LOG"
}

pair lfm25-8b-a1b LFM2.5-8B-A1B-Q8_0.gguf            8080 \
     lfm25-2.6b    LFM2.5-2.6B-Q8_0.gguf              8081

pair lfm25-1.2b    LFM2.5-1.2B-Instruct-Q8_0.gguf     8080 \
     bonsai2-9b    Ternary-Bonsai-2-9B-Q2_0.gguf      8081

solo bonsai2-4b    Ternary-Bonsai-2-4B-Q2_0.gguf      8080

dual lfm25-24b-a2b LFM2.5-24B-A2B-Q4_K_M.gguf         8080

echo "FRESH PANEL DONE $(date -Is)" >> "$LOG"
