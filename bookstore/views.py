import hmac
import os
import subprocess
import sys
from pathlib import Path

from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


def _run(*args):
    """Roda um comando na raiz do projeto e devolve a saída (levanta erro se falhar)."""
    result = subprocess.run(
        args,
        cwd=settings.BASE_DIR,
        capture_output=True,
        text=True,
        timeout=180,
        check=True,
    )
    return (result.stdout + result.stderr).strip()


@csrf_exempt
@require_POST
def update_server(request):
    """
    Endpoint de deploy, chamado pelo GitHub Actions após os testes passarem.

    Protegido por um token secreto (header X-Deploy-Token == env DEPLOY_TOKEN).
    Faz: git pull -> migrate -> collectstatic -> reload do app (touch no WSGI).
    """
    expected = os.environ.get("DEPLOY_TOKEN", "")
    received = request.headers.get("X-Deploy-Token", "")
    if not expected or not hmac.compare_digest(received.encode(), expected.encode()):
        return HttpResponseForbidden("Forbidden")

    python = os.environ.get("VENV_PYTHON") or str(Path(sys.prefix) / "bin" / "python")
    wsgi_file = os.environ.get("PA_WSGI_FILE")  # ex: /var/www/seuuser_pythonanywhere_com_wsgi.py
    branch = os.environ.get("DEPLOY_BRANCH", "main")

    steps = [
        ("git pull", ["git", "pull", "--ff-only", "origin", branch]),
        ("migrate", [python, "manage.py", "migrate", "--noinput"]),
        ("collectstatic", [python, "manage.py", "collectstatic", "--noinput"]),
    ]
    log = {}
    for name, cmd in steps:
        try:
            log[name] = _run(*cmd)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            log[name] = f"FALHOU: {getattr(exc, 'stderr', '') or exc}"
            return JsonResponse({"ok": False, "log": log}, status=500)

    # No PythonAnywhere, "tocar" o arquivo WSGI recarrega a aplicação.
    if wsgi_file:
        Path(wsgi_file).touch()
        log["reload"] = f"touch {wsgi_file}"
    else:
        log["reload"] = "PA_WSGI_FILE não definido: faça o Reload manualmente na aba Web"

    return JsonResponse({"ok": True, "log": log})
