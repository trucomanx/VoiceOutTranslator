#!/usr/bin/env python3
"""
Script para limpar sinks virtuais antigos (VirtualInput, VirtualInput.2, etc)
"""

import subprocess
import shlex

def run(cmd):
    proc = subprocess.run(
        shlex.split(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return proc.stdout.strip(), proc.returncode

def cleanup_virtual_sinks(prefix="VirtualInput"):
    """Remove todos os sinks com o prefixo especificado"""
    print(f"🧹 Limpando sinks com prefixo '{prefix}'...")
    
    # Listar todos os módulos
    modules_output, _ = run("pactl list short modules")

    modules = []
    for line in modules_output.splitlines():
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue
        modules.append(parts)

    removed_count = 0

    # 1️⃣ Remover loopbacks primeiro
    for module_id, module_name, args in modules:
        if module_name.startswith("module-loopback"):
            if f"sink={prefix}" in args:
                print(f"  🗑️  Removendo loopback {module_id}")
                subprocess.run(
                    ["pactl", "unload-module", module_id],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                removed_count += 1

    # 2️⃣ Depois remover null-sinks
    for module_id, module_name, args in modules:
        if module_name.startswith("module-null-sink"):
            if f"sink_name={prefix}" in args:
                print(f"  🗑️  Removendo null-sink {module_id}")
                subprocess.run(
                    ["pactl", "unload-module", module_id],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                removed_count += 1
    
    if removed_count == 0:
        print(f"  ✅ Nenhum sink com prefixo '{prefix}' encontrado")
    else:
        print(f"  ✅ {removed_count} módulo(s) removido(s)")
    
    return removed_count

if __name__ == "__main__":
    print("=" * 60)
    print("LIMPEZA DE SINKS VIRTUAIS")
    print("=" * 60)
    
    # Limpar VirtualInput
    cleanup_virtual_sinks("VirtualInput")
    
    # Opcional: limpar VirtualOutput também
    print()
    resposta = input("Deseja limpar VirtualOutput também? (s/N): ").strip().lower()
    if resposta == 's':
        cleanup_virtual_sinks("VirtualOutput")
    
    print("\n" + "=" * 60)
    print("✅ Limpeza concluída!")
    print("=" * 60)
