#!/bin/bash
set -e

dbt clean
dbt deps
dbt build
dbt docs generate
dbt docs serve

exec "$@"
