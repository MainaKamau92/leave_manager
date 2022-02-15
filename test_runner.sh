export ENVIRONMENT=testing
_=$1

coverage run -m pytest --reuse-db "$1"

[ -z "$1" ] && coverage report json
