import os
from unittest.mock import patch

from pico.config import find_pico_project_root, load_pico_env


def test_find_pico_project_root_points_at_repo_root():
    root = find_pico_project_root()

    assert root is not None
    assert (root / "pyproject.toml").exists()
    assert (root / "pico" / "config.py").exists()


def test_load_pico_env_reads_install_root_env(tmp_path):
    pico_root = tmp_path / "pico-main"
    pico_root.mkdir()
    (pico_root / ".env").write_text("PICO_DEEPSEEK_API_KEY=sk-from-pico\n", encoding="utf-8")

    with patch.dict(os.environ, {}, clear=True):
        with patch("pico.config.find_pico_project_root", return_value=pico_root):
            loaded = load_pico_env()

    assert loaded["PICO_DEEPSEEK_API_KEY"] == "sk-from-pico"
