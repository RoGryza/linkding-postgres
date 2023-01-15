This fork is unmaintaineed. Postgres support was added upstream in [linkding#388](https://github.com/sissbruecker/linkding/pull/388), published with [v1.16.0](https://github.com/sissbruecker/linkding/releases/tag/v1.16.0)

NOTE: this is a fork of the official linkding with added PostgreSQL support. See [the original
repo](https://github.com/sissbruecker/linkding), this repository only documents changes from
the original project so reading the documentation there is recommended. Do not file issues there
unless you're sure they're not caused by the changes in this fork, if in doubt feel free to open an
issue here and I can help look into it.

Note that this fork does not support SQLite in order to ease maintenance.

## Docker

There is an example `docker-compose.yml` file. Copy the `.env.sample` file to `.env` and set your
parameters, then run:
```shell
docker-compose up -d
```

Afterwards, follow [User setup](https://github.com/sissbruecker/linkding#user-setup) from the
official linkding docs.

##  Configuration

Linkding-postgres is configured via the following environment variables (see
`sitreoot/settings/base.py`):

| Variable       | Default   | Description       |
| -------------- | --------- | ----------------- |
| LD_DB_NAME     | linkding  | Database name     |
| LD_DB_USER     | postgres  | Postgres user     |
| LD_DB_PASSWORD | postgres  | Postgres password |
| LD_DB_HOST     | localhost | Postgres host     |
| LD_DB_PORT     | 5432      | Postgres port     |

Alternatively, you can update `DATABASES['default']` in `siteroot/settings/custom.py`. See
[`siteroot/settings/base.py`](https://github.com/RoGryza/linkding-postgres/tree/master/siteroot/settings/base.py)
for an example.

###  Testing

Tests depend on a postgres instance running. If you have docker You can run `run-test-postgres.sh`
to start it with the correct credentials in the background. Note that the script will fail if port
`5432` is not free, e.g. if you have another instance of postgres running on the default port. See
`DATABASES` in `siteroot/settings/base.py` for the expected default credentials.

Alternatively if you have [`direnv`](https://github.com/direnv/direnv) and PostgreSQL installed
locally, you can just run `postgres` inside the direnv setup by `.envrc`.
