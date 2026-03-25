# #!/usr/bin/env bash
# # Arranque: runserver + túnel Serveo (reinicia o SSH se cair).
# # Requer: Python com dependências (preferir pasta .venv neste directório).
# set -u

# ROOT="$(cd "$(dirname "$0")" && pwd)"
# cd "$ROOT" || exit 1

# # Activa apenas se o script existir (nunca falha por falta de venv)
# if [[ -r ".venv/bin/activate" ]]; then
#   # shellcheck source=/dev/null
#   . ".venv/bin/activate"
# elif [[ -r "venv/bin/activate" ]]; then
#   # shellcheck source=/dev/null
#   . "venv/bin/activate"
# fi

# python3 manage.py runserver 0.0.0.0:3479

# # Keepalive: reduz quedas do túnel durante uploads longos (ZIP/PDF).
# SERVEO_SSH_OPTS=(
#   -o ServerAliveInterval=15
#   -o ServerAliveCountMax=12
#   -o TCPKeepAlive=yes
# )

# while true; do
#   ssh "${SERVEO_SSH_OPTS[@]}" -R caf:80:localhost:3479 serveo.net
#   echo "Serveo caiu, a reconectar em 5s..."
#   sleep 5
# done
# (opcional) ativar o venv, se estiver a usar
# source venv/bin/activate

# 1) subir a API na porta 8001 em background
# python3 manage.py runserver 0.0.0.0:8001 &

# 2) túnel Serveo que reconecta sempre que cair
while true; do
  ssh -R frota:80:localhost:8001 serveo.net
  echo "Serveo caiu, a reconectar em 5s..."
  sleep 5
done
