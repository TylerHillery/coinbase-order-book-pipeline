#!/bin/bash
set -e

dbt deps
dbt build
dbt docs generate
dbt docs serve

exec "$@"
