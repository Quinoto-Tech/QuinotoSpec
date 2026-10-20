#!/usr/bin/env python3
"""quinotospec-complexity-router — routing adaptativo por complejidad.

Clasifica el alcance de un cambio en uno de 4 tracks:
    quick_fix < simple < complex < enterprise

Uso:
    router.py --files 2 --services 1 --json
    router.py --files 1 --description "typo en el README"
    router.py --files 30 --services 3 --regulated --json
    router.py --override complex --json
"""

import argparse
import json
import re
import sys

sys.dont_write_bytecode = True

TRACKS = ("quick_fix", "simple", "complex", "enterprise")

TRACK_METADATA = {
    "quick_fix": {
        "label": "Quick Fix",
        "depth": "Spec minima -> implementacion directa",
        "workflow": "/quinotospec.fix",
        "needs_proposal": False,
        "gates": ["tests", "validate"],
    },
    "simple": {
        "label": "Simple",
        "depth": "Tech-spec ligera -> tasks -> implementacion",
        "workflow": "/quinotospec.quick-dev",
        "needs_proposal": False,
        "gates": ["tdd", "verify-before-done", "validate"],
    },
    "complex": {
        "label": "Complex",
        "depth": "Spec -> design -> US -> tasks -> implementacion",
        "workflow": "/quinotospec.create-proposal",
        "needs_proposal": True,
        "gates": ["tdd", "verify-before-done", "validate", "review"],
    },
    "enterprise": {
        "label": "Enterprise",
        "depth": "SDLC completo + constitution gates + compliance",
        "workflow": "/quinotospec.flow",
        "needs_proposal": True,
        "gates": [
            "constitution",
            "tdd",
            "verify-before-done",
            "validate",
            "review",
            "heimdallr",
            "human-approval",
        ],
    },
}

QUICK_KEYWORDS = ("typo", "readme", "doc", "comentario", "comment", "log", "config", "lint")
ENTERPRISE_KEYWORDS = ("regulated", "compliance", "pci", "hipaa", "gdpr", "multi-team", "migration")
COMPLEX_KEYWORDS = ("auth", "database", "schema", "api", "migration", "payment", "security")


def bump(current, target):
    return target if TRACKS.index(target) > TRACKS.index(current) else current


def classify(args):
    rationale = []
    signals = {
        "files": args.files,
        "services": args.services,
        "teams": args.teams,
        "db": args.db,
        "auth": args.auth,
        "public_api": args.public_api,
        "regulated": args.regulated,
    }

    if args.files <= 1:
        track = "quick_fix"
        rationale.append("{} archivo(s): alcance acotado a un cambio puntual.".format(args.files))
    elif args.files <= 3:
        track = "simple"
        rationale.append("{} archivos: feature pequena o ajuste localizado.".format(args.files))
    elif args.files <= 10:
        track = "complex"
        rationale.append("{} archivos: cambio multi-archivo.".format(args.files))
    else:
        track = "enterprise"
        rationale.append("{} archivos: alcance amplio, requiere planificacion completa.".format(args.files))

    if args.services > 1:
        track = bump(track, "complex")
        rationale.append("{} servicios afectados: se requiere coordinacion entre componentes.".format(args.services))
    if args.services > 2:
        track = bump(track, "enterprise")
        rationale.append("{} servicios: alcance distribuido.".format(args.services))
    if args.teams > 1:
        track = bump(track, "complex")
        rationale.append("{} equipos involucrados: coordinacion multi-equipo.".format(args.teams))

    if args.db:
        track = bump(track, "complex")
        rationale.append("Cambio de base de datos o migracion de datos detectado.")
    if args.auth:
        track = bump(track, "complex")
        rationale.append("Cambio en autenticacion/autorizacion detectado.")
    if args.public_api:
        track = bump(track, "complex")
        rationale.append("Cambio de API publica: requiere contrato y compatibilidad.")
    if args.regulated:
        track = bump(track, "enterprise")
        rationale.append("Contexto regulado o de compliance: gates adicionales obligatorios.")

    description = (args.description or "").lower()
    if description:
        if any(word in description for word in ENTERPRISE_KEYWORDS):
            track = bump(track, "enterprise")
            rationale.append("La descripcion menciona terminos de compliance/regulacion.")
        elif any(word in description for word in COMPLEX_KEYWORDS):
            track = bump(track, "complex")
            rationale.append("La descripcion menciona auth/datos/API/seguridad.")
        elif any(word in description for word in QUICK_KEYWORDS) and args.services <= 1 and not (
            args.db or args.auth or args.public_api or args.regulated
        ):
            track = bump(track, "quick_fix") if track == "simple" else track
            rationale.append("La descripcion sugiere un cambio trivial (docs/config/typo).")

    if args.override:
        track = args.override
        rationale.append("Track forzado manualmente con --override {}.".format(args.override))

    metadata = TRACK_METADATA[track]
    return {
        "schema_version": 1,
        "track": track,
        "label": metadata["label"],
        "depth": metadata["depth"],
        "needs_proposal": metadata["needs_proposal"],
        "recommended_workflow": metadata["workflow"],
        "gates": metadata["gates"],
        "signals": signals,
        "rationale": rationale,
    }


def render(report):
    lines = [
        "Quinotospec Complexity Router",
        "",
        "Track: {} ({})".format(report["track"], report["label"]),
        "Profundidad: {}".format(report["depth"]),
        "Workflow recomendado: {}".format(report["recommended_workflow"]),
        "Requiere propuesta formal: {}".format("si" if report["needs_proposal"] else "no"),
        "Gates: {}".format(", ".join(report["gates"])),
        "",
        "Razonamiento:",
    ]
    for reason in report["rationale"]:
        lines.append("  - " + reason)
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Router adaptativo de complejidad (Quick Fix / Simple / Complex / Enterprise)"
    )
    parser.add_argument("--files", type=int, default=1, help="Archivos estimados a tocar")
    parser.add_argument("--services", type=int, default=1, help="Servicios afectados")
    parser.add_argument("--teams", type=int, default=1, help="Equipos involucrados")
    parser.add_argument("--db", action="store_true", help="Cambios de base de datos o migraciones")
    parser.add_argument("--auth", action="store_true", help="Cambios de autenticacion/autorizacion")
    parser.add_argument("--public-api", action="store_true", help="Cambios de API publica")
    parser.add_argument("--regulated", action="store_true", help="Contexto regulado/compliance")
    parser.add_argument("--description", default="", help="Descripcion libre del cambio")
    parser.add_argument("--override", choices=TRACKS, help="Forzar un track")
    parser.add_argument("--json", action="store_true", help="Salida JSON")
    args = parser.parse_args(argv)

    if args.files < 0 or args.services < 0 or args.teams < 0:
        print("ERROR: --files/--services/--teams must be >= 0", file=sys.stderr)
        return 2

    report = classify(args)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
