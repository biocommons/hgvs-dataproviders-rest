"""Test across supported Python versions declared by pyproject.toml."""

import nox

nox.options.default_venv_backend = "uv"
nox.options.reuse_venv = "yes"

PYTHON_VERSIONS = nox.project.python_versions(nox.project.load_toml("pyproject.toml"))


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run the test suite in an environment synced from uv.lock."""
    env = {"UV_PROJECT_ENVIRONMENT": session.virtualenv.location}
    session.run_install(
        "uv", "sync", "--locked", f"--python={session.virtualenv.location}", env=env
    )
    session.run("make", "test", env=env, external=True)
