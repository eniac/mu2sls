#!/bin/bash

echo "Python tests"
python3 -m pytest

export MU2SLS_TOP=${MU2SLS_TOP:-$(git rev-parse --show-toplevel --show-superproject-working-tree)/mu2sls}

test_log_dir="${MU2SLS_TOP}/tests/logs/"
mkdir -p "${test_log_dir}"
test_log="${test_log_dir}/test_media_service.log"

echo "Application integration tests... logs in \"${test_log}\""
./tests/test_media_service.sh >"${test_log}" 2>&1 || echo "Error: Media service test failed"
