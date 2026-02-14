#!/usr/bin/python3

import subprocess
import shlex


def _run(cmd: str) -> str:
    """Executa comando e retorna stdout ou lança exceção"""
    proc = subprocess.run(
        shlex.split(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if proc.returncode != 0:
        error_msg = proc.stderr.strip()
        raise RuntimeError(f"Comando \n'{cmd}' \nfalhou: \n{error_msg}")
    return proc.stdout.strip()


def setup_virtual_input(
    virtual_sink: str = "VirtualInput",
    latency_msec: int = 1
) -> dict:
    """
    Idempotente:
    - cria VirtualInput se não existir
    - cria loopback da entrada padrão para ele se não existir
    - não duplica nada
    """

    created = {}

    # 1️⃣ entrada padrão (idioma-agnóstico)
    default_source = _run("pactl get-default-source")

    # 2️⃣ verificar se o sink virtual já existe
    sinks = _run("pactl list short sinks")
    sink_exists = any(
        line.split()[1] == virtual_sink
        for line in sinks.splitlines()
    )

    if not sink_exists:
        module_id = _run(
            f"pactl load-module module-null-sink sink_name={virtual_sink}"
        )
        created["null_sink"] = int(module_id)

    # 3️⃣ verificar se já existe loopback correto
    modules = _run("pactl list short modules")

    loopback_exists = False
    for line in modules.splitlines():
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue

        _, module_name, args = parts

        if module_name != "module-loopback":
            continue

        if (
            f"source={default_source}" in args
            and f"sink={virtual_sink}" in args
        ):
            loopback_exists = True
            break

    if not loopback_exists:
        module_id = _run(
            "pactl load-module module-loopback "
            f"source={default_source} "
            f"sink={virtual_sink} "
            f"latency_msec={latency_msec}"
        )
        created["loopback"] = int(module_id)

    return created


def teardown_virtual_input(created: dict):
    for module_id in created.values():
        subprocess.run(
            ["pactl", "unload-module", str(module_id)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
