#!/usr/bin/env bash
# Panel: eight popular models, each at the best quantisation that fits one 12 GB
# card at 16,384 context. Two models per wave, one per card, one run per task.
set -u

MODELS=$HOME/.cache/llama-models
OUT=/home/hati/.hermes/cache/scratch/smallbench
LOG=$OUT/progress.log
mkdir -p "$OUT/runs"

wait_file() {
    local file=$1 have
    for _ in $(seq 1 300); do
        if [[ -f "$MODELS/$file.done" ]]; then
            echo "ready $file $(stat -c%s "$MODELS/$file")" >> "$LOG"
            return 0
        fi
        have=$(stat -c%s "$MODELS/$file" 2>/dev/null || echo 0)
        echo "waiting $file $((have/1000000)) MB" >> "$LOG"
        sleep 20
    done
    echo "timeout $file" >> "$LOG"
    return 1
}

wave() {  # name file dev port name file dev port
    local n1=$1 f1=$2 d1=$3 p1=$4 n2=$5 f2=$6 d2=$7 p2=$8
    wait_file "$f1" || return 1
    wait_file "$f2" || return 1
    bash /home/hati/.local/share/modelbench-x/run_wave.sh \
        "$n1" "$MODELS/$f1" "$d1" "$p1" "$n2" "$MODELS/$f2" "$d2" "$p2" 1
}

wave qwen3-14b  Qwen3-14B-Q4_K_M.gguf                CUDA0 8080 \
     gemma3-12b gemma-3-12b-it-Q5_K_M.gguf           CUDA1 8081

wave qwen25-14b Qwen2.5-14B-Instruct-Q4_K_M.gguf     CUDA0 8080 \
     qwen3-8b   Qwen3-8B-Q8_0.gguf                   CUDA1 8081

wave llama31-8b Meta-Llama-3.1-8B-Instruct-Q8_0.gguf CUDA0 8080 \
     qwen25coder-7b Qwen2.5-Coder-7B-Instruct-Q8_0.gguf CUDA1 8081

wave mistral-7b Mistral-7B-Instruct-v0.3-Q8_0.gguf   CUDA0 8080 \
     deepseek-r1-7b DeepSeek-R1-Distill-Qwen-7B-Q8_0.gguf CUDA1 8081

echo "PANEL DONE $(date -Is)" >> "$LOG"
