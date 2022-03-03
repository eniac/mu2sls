#!/bin/bash

echo "Python tests"
python3 -m pytest

export MU2SLS_TOP=${MU2SLS_TOP:-$(git rev-parse --show-toplevel --show-superproject-working-tree)/mu2sls}

test_log_dir="${MU2SLS_TOP}/tests/logs/"
mkdir -p "${test_log_dir}"
test_log="${test_log_dir}/test_media_service.log"

echo "Application integration tests... logs in \"${test_log}\""
echo "Media service with local store..."
./tests/test_media_service.sh >"${test_log}" 2>&1 || { echo "Error: Media service test failed"; exit 1; }
#echo "Media service with local Beldi FDB store..."
#./tests/test_media_service.sh beldi >>"${test_log}" 2>&1 || { echo "Error: Media service test (with beldi) failed"; exit 1; }

echo "Cross Service Transactions with local store..."
./tests/test_cross_service_txn.sh >"${test_log}" 2>&1 || { echo "Error: Cross Service Transactions test failed"; exit 1; }
