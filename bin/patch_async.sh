#! /usr/bin/env bash

PYTHON_SITE_PACKAGES_FIND_PATTERN='lib/python*/site-packages'
PYTHON_BIN_REL_DIR="bin/python"

find_python_bin() {
    local python_bin
    python_bin="$1"
    if [ -z "$python_bin" ]; then
        if [ -z "$VIRTUAL_ENV" ]; then
            echo "'VIRUAL_ENV' variable isn't set" && return 1
        else
            python_bin="$VIRTUAL_ENV/bin/python"
        fi
    fi
    [ ! -e "$python_bin" ] \
        && echo "Python binary '$python_bin' doesn't exist" && return 2
    echo "$python_bin"
}

find_python_lib_dir() {
    local python_lib_dir
    python_lib_dir="$1"
    if [ -z "$python_lib_dir" ]; then
        if [ -z "$VIRTUAL_ENV" ]; then
            echo "'VIRUAL_ENV' variable isn't set" && return 1
        else
            python_lib_dir="$VIRTUAL_ENV/lib"
        fi
    fi
    [ ! -e "$python_lib_dir" ] \
        && echo "Python library dir '$python_lib_dir' doesn't exist" && return 2
    echo "$python_lib_dir"
}

get_python_maj_min_ver() {
    local python_bin python_lib_dir python_full_ver python_maj_min_ver
    python_bin="$(find_python_bin "$1")" || return $?
    [ -z "$python_bin" ] && echo "Path to python bin isn't set" && return 1
    python_lib_dir="$(find_python_lib_dir "$2")" || return $?
    [ -z "$python_lib_dir" ] && echo "Path to python lib isn't set" && return 2

    python_full_ver="$("$python_bin" --version | head -1 | awk '{print $2}')"
    python_maj_min_ver="${python_full_ver%.*}"
    echo "$python_maj_min_ver"
}

get_python_sp_dir() {
    local python_lib_dir python_maj_min_ver python_sp_dir
    python_lib_dir="$(find_python_lib_dir "$1")"
    [ -z "$python_lib_dir" ] && echo "Path to python lib isn't set" && return 1
    python_bin="$(find_python_bin "$2")"
    [ -z "$python_bin" ] && echo "Path to python bin isn't set" && return 2
    python_maj_min_ver="$(get_python_maj_min_ver "$python_bin" "$python_lib_dir")"
    [ -z "$python_maj_min_ver" ] && echo "Python major.minor version isn't set" && return 3

    python_sp_dir="$python_lib_dir/python${python_maj_min_ver}/site-packages"
    [ ! -e "$python_sp_dir" ] \
        && echo "Python site-packages dir '$python_sp_dir' doesn't exist" \
        && return 3
    echo "$python_sp_dir"
}

do_patch_celery() {
    local python_sp_dir celery_redis_dir
    python_sp_dir="$(get_python_sp_dir "$1" "$2")"
    [ -z "$python_sp_dir" ] \
        && echo "Path to python site-packages bin isn't set" \
        && return 1
    celery_redis_dir="$python_sp_dir/celery/backends"
    echo "Celery Redis dir: '$celery_redis_dir'"
    (cd "$celery_redis_dir" \
        && if [ -e async.py ]; then
            echo -n "Moving 'async.py' to 'asynchronous.py' ... " \
            && mv async.py asynchronous.py \
            && echo "OK" \
            && echo -n "Replacing 'async' to 'asynchronous' in 'redir.py ... " \
            && ([  -e redis.py.bak ] || sed -i .bak 's/async/asynchronous/g' redis.py ) \
            && echo "OK" \
            && echo -n "Replacing 'async' to 'asynchronous' in 'rpc.py ... " \
            && ([ -e rpc.py.bak ] || sed -i .bak 's/async/asynchronous/g' rpc.py ) \
            && echo "OK"
        fi
    )
}

do_patch_astunparse() {
    local python_sp_dir celery_redis_dir
    python_sp_dir="$(get_python_sp_dir "$1" "$2")"
    [ -z "$python_sp_dir" ] \
        && echo "Path to python site-packages bin isn't set" \
        && return 1
    astunparse_dir="$python_sp_dir/astunparse"
    echo "astunparse dir: '$astunparse_dir'"
    (cd "$astunparse_dir" \
        && if [ -e unparser.py ]; then
            echo -n "Replacing 'async' to 'asynchronous' in 'unparser.py' ... " \
            && sed -i .bak 's/async/asynchronous/g' unparser.py \
            && echo "OK"
        fi
    )
}

do_patch() {
    do_patch_celery && do_patch_astunparse
}

show_help() {
    echo
    echo "Usage: $(basename $0) <find|patch|help>"
    echo
    echo "Activate virtual env and run '$(basename "$0") patch'"
    echo
}

[ "$0" = "$BASH_SOURCE" ] && case "$1" in
    find) find_python_bin "$2" "$3" ;;
    patch) do_patch ;;
    *) show_help ;;
esac
