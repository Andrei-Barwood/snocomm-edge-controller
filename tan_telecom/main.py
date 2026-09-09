#!/usr/bin/env python3
"""
Punto de entrada de TAN-Telecom.

Uso:
    python main.py --help
    python main.py --example small
    python main.py --potencia-kw 45 --num-racks 4 --redundancia N
"""

from __future__ import annotations

def main() -> None:
    """Lanza la CLI Typer."""
    from .cli import run

    run()


if __name__ == "__main__":
    main()
