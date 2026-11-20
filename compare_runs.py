import os
import csv
import json
import hashlib

REPO_ROOT = os.getcwd()
BASE_DIR = os.path.join(REPO_ROOT, "output")
RUN_DIR = os.path.join(REPO_ROOT, "ptd_output", "output")

if not os.path.exists(RUN_DIR):
    print("ERRO: Diretório ptd_output/output/ não encontrado. Execute o pipeline primeiro.")
    exit(1)

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def line_count(path):
    with open(path, "rb") as f:
        return sum(1 for _ in f)

CSVS = [
    "organs.csv",
    "risks.csv",
    "deliveries.csv",
    "pdf_metadata.csv",
    "vocabulary_mapping.csv",
    "error_report.csv",
]

print("=" * 80)
print(f"{'ARQUIVO CSV':<25} | {'LINHAS (ORIGINAL)':<18} | {'LINHAS (LOCAL)':<15} | {'STATUS HASH'}")
print("-" * 80)

for fname in CSVS:
    base_p = os.path.join(BASE_DIR, fname)
    run_p = os.path.join(RUN_DIR, fname)
    
    if not os.path.exists(run_p):
        print(f"{fname:<25} | {'OK':<18} | {'AUSENTE':<15} | FALHA")
        continue

    lines_base = line_count(base_p)
    lines_run = line_count(run_p)
    hash_match = "IDÊNTICO" if sha256(base_p) == sha256(run_p) else "DIFERENTE (ver notas)"
    
    print(f"{fname:<25} | {lines_base:<18} | {lines_run:<15} | {hash_match}")

print("=" * 80)

# Comparação do Quality Gate
print("\nCOMPARAÇÃO DAS MÉTRICAS DO VALIDATION REPORT:")
with open(os.path.join(BASE_DIR, "validation_report.json")) as f:
    orig_rep = json.load(f)
with open(os.path.join(RUN_DIR, "validation_report.json")) as f:
    run_rep = json.load(f)

for metric in ["orgaos", "entregas", "riscos", "errors"]:
    orig_val = orig_rep["counts"].get(metric)
    run_val = run_rep["counts"].get(metric)
    match_str = "✓ IGUAL" if orig_val == run_val else f"≠ DIFERENTE (orig={orig_val}, run={run_val})"
    print(f"  - {metric.capitalize():<12}: {orig_val:>5} vs {run_val:>5}  -> {match_str}")
