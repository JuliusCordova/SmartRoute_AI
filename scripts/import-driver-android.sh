#!/usr/bin/env bash
# Importar el ZIP revisado de Android Studio al monorepo SmartRoute AI.
# Uso: bash scripts/import-driver-android.sh /ruta/SmartRoute_AI_Android_Driver_US011_revisado.zip
set -euo pipefail
ZIP="${1:-}"
[[ -n "$ZIP" && -f "$ZIP" ]] || { echo "Uso: $0 archivo.zip" >&2; exit 2; }
[[ "$(git branch --show-current)" == "feat/mobile-driver-android-base" ]] || {
  echo "ERROR: cambie primero a feat/mobile-driver-android-base (no editar main)" >&2; exit 1;
}
[[ -z "$(git status --porcelain --untracked-files=no)" ]] || {
  echo "ERROR: existen cambios rastreados sin confirmar; inspeccione git status" >&2; exit 1;
}
python3 - "$ZIP" <<'PY'
import sys, zipfile
from pathlib import Path
archive=Path(sys.argv[1])
root=Path.cwd().resolve()
with zipfile.ZipFile(archive) as z:
    entries=[i for i in z.infolist() if not i.is_dir()]
    for info in entries:
        path=Path(info.filename)
        if len(path.parts)<3 or path.parts[:2]!=("apps","driver-android"):
            raise SystemExit(f"ERROR: ruta fuera del módulo móvil: {path}")
        if ".." in path.parts or path.is_absolute():
            raise SystemExit(f"ERROR: ruta no permitida: {path}")
        if any(x in path.parts for x in (".gradle",".kotlin","build",".idea")):
            raise SystemExit(f"ERROR: archivo de build o configuración local: {path}")
        if path.name in ("google-services.json","local.properties"):
            raise SystemExit(f"ERROR: se detectó un secreto o configuración local: {path}")
        if (info.external_attr>>16)&0o170000==0o120000:
            raise SystemExit(f"ERROR: enlace simbólico en ZIP: {path}")
    for info in entries:
        destination=root / info.filename
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(z.read(info))
print(f"Importados {len(entries)} archivos en apps/driver-android/")
PY
git add apps/driver-android
echo "Archivos preparados para commit:"
git diff --cached --stat
echo "Revise git diff --cached antes de crear commit y push."
