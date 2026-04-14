[![Mentioned in Awesome FastAPI](https://awesome.re/mentioned-badge.svg)](https://github.com/mjhea0/awesome-fastapi?tab=readme-ov-file#best-practices)

Stay tuned. Refactor in progress, see [`legacy-2025`](https://github.com/ivan-borovets/fastapi-clean-example/tree/legacy-2025) branch for architecture docs

TODO:
- [x] Write tests
- [ ] Explain code and patterns in new README
- [ ] Make template project

Prerequisites
```shell
uv sync
source .venv/bin/activate
pre-commit install --hook-type pre-commit --hook-type pre-push
```

Start in Docker
```shell
make upd
```

Start locally
```shell
make upd-local
alembic upgrade head
uvicorn app.main.run:make_app --host 0.0.0.0 --port 8000 --reload
# or `src/app/main/run.py` in IDE
```
Full API access:
- create user via sign up
- set its role to `super_admin` manually in DB
- log in as super admin

Stop
```shell
make down
```

Test (light paths)
```shell
make check
```

Test (all paths)
```shell
make test-docker
```

See [Makefile](Makefile) for more commands

Thanks for your patience and support

[Acknowledgements](https://github.com/ivan-borovets/fastapi-clean-example/tree/legacy-2025?tab=readme-ov-file#acknowledgements)
