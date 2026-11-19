#!/bin/sh
set -eu

# Native Render ONNX runtime. Development/optional embedding packages stay in CI.
python -m pip install --upgrade pip
python -m pip install -r requirements.production.txt
python -m pip check
# Names and versions only, without installation URLs or environment values.
python -m pip list --format=json

# Audit the complete installed runtime before Render activates the build.
# Keep the audit tooling in its own disposable environment.
audit_root=$(mktemp -d)
trap 'rm -rf "$audit_root"' EXIT
python -m pip freeze --all > "$audit_root/runtime.txt"
python -m venv "$audit_root/auditor"
"$audit_root/auditor/bin/python" -m pip install pip-audit==2.10.1
"$audit_root/auditor/bin/python" -m pip_audit --strict \
    --requirement "$audit_root/runtime.txt" --progress-spinner off
