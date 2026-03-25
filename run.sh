#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT" || exit 1

# Ambiente virtual (tenta .venv primeiro, depois venv)
if [[ -f ".venv/bin/activate" ]]; then
  # shellcheck source=/dev/null
  source ".venv/bin/activate"
elif [[ -f "venv/bin/activate" ]]; then
  # shellcheck source=/dev/null
  source "venv/bin/activate"
fi

# 1) subir a API na porta 3479 em background
python3 manage.py runserver 0.0.0.0:3479 &

# 2) túnel Serveo que reconecta sempre que cair
while true; do
  ssh -R caf:80:localhost:3479 serveo.net
  echo "Serveo caiu, a reconectar em 5s..."
  sleep 5
done
