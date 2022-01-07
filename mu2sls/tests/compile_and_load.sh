
input=${1?Source Service not given}
output_name="test_compiled_service_module"
output_file="${output_name}.py"

export MU2SLS_TOP=${MU2SLS_TOP:-$(git rev-parse --show-toplevel --show-superproject-working-tree)/mu2sls}


python3 "${MU2SLS_TOP}/mu2sls" "${input}" "${output_file}"
python3 -i -c "from scripts import local_dev; module = local_dev.import_compiled(\"${output_name}\"); store = local_dev.init_local_store()"
