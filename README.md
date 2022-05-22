NOTE: this is a fork of the official linkding with added PostgreSQL support. See [the original
repo](https://github.com/sissbruecker/linkding), this repository only documents changes from
the original project so reading the documentation there is recommended. Do not file issues there
unless you're sure they're not caused by the changes in this fork, if in doubt feel free to open an
issue here and I can help look into it.

Note that this fork does not support SQLite for easier maintenance.

##  TODO

##  Development

###  Testing

Tests depend on a postgres instance running. If you have docker You can run `run-test-postgres.sh`
to start it with the correct credentials in the background. Note that the script will fail if port
`5432` is not free, e.g. if you have another instance of postgres running on the default port. See
`DATABASES` in `siteroot/settings/base.py` for the expected default credentials.
