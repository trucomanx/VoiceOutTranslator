#!/usr/bin/python3

import subprocess
import shlex


def _run(cmd: str) -> str:
    proc = subprocess.run(
        shlex.split(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())
    return proc.stdout.strip()


def setup_virtual_output(
    virtual_sink: str = "VirtualOutput",
    latency_msec: int = 1
) -> dict:
    """
    Idempotente:
    - cria VirtualOutput se não existir
    - cria loopback da saída padrão para ele se não existir
    - não duplica nada
    """

    created = {}

    # 1️⃣ saída padrão (idioma-agnóstico)
    default_sink = _run("pactl get-default-sink")
    monitor_source = f"{default_sink}.monitor"

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
            f"source={monitor_source}" in args
            and f"sink={virtual_sink}" in args
        ):
            loopback_exists = True
            break

    if not loopback_exists:
        module_id = _run(
            "pactl load-module module-loopback "
            f"source={monitor_source} "
            f"sink={virtual_sink} "
            f"latency_msec={latency_msec}"
        )
        created["loopback"] = int(module_id)

    return created


def teardown_virtual_output(created: dict):
    for module_id in created.values():
        subprocess.run(
            ["pactl", "unload-module", str(module_id)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

