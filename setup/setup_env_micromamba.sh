#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./setup_env.sh /desired/base/path/sim_env
# If no path is given, defaults to ./sim_env

base_prefix="${1:-$(pwd)/sim_env}"
base_prefix="$(python - <<'PY' "$base_prefix"
import os, sys
print(os.path.abspath(sys.argv[1]))
PY
)"

env_prefix="$base_prefix"
counter=1

# Check if a micromamba environment already exists at a given prefix
env_exists() {
    local prefix="$1"
    [[ -d "$prefix" ]] && return 0

    # Also check micromamba's registered env list
    micromamba env list | awk '{print $NF}' | grep -Fxq "$prefix"
}

# Increment env path until an unused one is found
while env_exists "$env_prefix"; do
    env_prefix="${base_prefix}${counter}"
    ((counter++))
done

created_at_utc="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
created_at_local="$(date +"%Y-%m-%dT%H:%M:%S%z")"

echo "Creating micromamba environment at:"
echo "  $env_prefix"

# Create the micromamba environment by prefix/path
micromamba create --prefix "$env_prefix" python=3.11 -y

echo "Created micromamba environment:"
echo "  $env_prefix"
echo "Installing packages..."

eval "$(micromamba shell hook --shell bash)"
micromamba activate "$env_prefix"

# Keep micromamba for micromamba packages, pip for pip packages
micromamba install --prefix "$env_prefix" -y compilers meson git
pip install numpy scipy matplotlib h5py cython ipython pyklu

echo "Downloading scripts..."

cd $env_prefix
mkdir -p ./PyCOMPLETE
cd ./PyCOMPLETE
scripts_path="$(pwd)"

git clone https://github.com/ekatralis/PyECLOUD
git clone https://github.com/ekatralis/PyPIC
git clone https://github.com/ekatralis/PyHEADTAIL
git clone https://github.com/pycomplete/NAFFlib
git clone https://github.com/ekatralis/PyPARIS
git clone https://github.com/ekatralis/PyPARIS_sim_class
git clone https://github.com/pycomplete/PyPARIS_CoupledBunch_sim_class

cd PyECLOUD
./setup_pyecloud
cd ..

cd PyPIC
git switch replace_bool_idx
make
cd ..

cd PyHEADTAIL
git switch fix_installation_scripts
make
cd ..

cd PyPARIS
git switch prevent_infinite_hangs_in_multiproc
cd ..

cd NAFFlib/NAFFlib
make py3
cd ../../

# Detect site-packages path dynamically from the active env
site_packages="$(
python - <<'PY'
import site
paths = site.getsitepackages()
print(paths[0] if paths else "")
PY
)"

if [[ -z "$site_packages" || ! -d "$site_packages" ]]; then
    echo "Could not determine site-packages path" >&2
    exit 1
fi

cat <<EOF > "$site_packages/local-packages.pth"
$scripts_path
$scripts_path/PyHEADTAIL
$scripts_path/NAFFlib
EOF

echo "Added scripts to:"
cat "$site_packages/local-packages.pth"

# -------------------------------------------------------------------
# Metadata collection
# -------------------------------------------------------------------

metadata_dir="$env_prefix/environment_metadata"
mkdir -p "$metadata_dir"

metadata_file="$metadata_dir/ENVIRONMENT_METADATA.txt"
pip_freeze_file="$metadata_dir/pip_freeze.txt"
micromamba_list_file="$metadata_dir/micromamba_list.txt"
micromamba_export_file="$metadata_dir/micromamba_env_export.yml"
git_report_file="$metadata_dir/git_repos_report.txt"

# Raw package inventories
pip freeze > "$pip_freeze_file"
micromamba list --prefix "$env_prefix" > "$micromamba_list_file"
micromamba env export --prefix "$env_prefix" > "$micromamba_export_file"

# Git repo metadata
{
    echo "Git repository metadata"
    echo "Generated at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    echo

    for repo in \
        PyECLOUD \
        PyPIC \
        PyKLU \
        PyHEADTAIL \
        NAFFlib \
        PyPARIS \
        PyPARIS_sim_class \
        PyPARIS_CoupledBunch_sim_class
    do
        if [[ -d "$scripts_path/$repo/.git" ]]; then
            echo "============================================================"
            echo "Repository: $repo"
            echo "Path: $scripts_path/$repo"
            echo "Remote(s):"
            git -C "$scripts_path/$repo" remote -v || true
            echo
            echo "Current branch:"
            git -C "$scripts_path/$repo" branch --show-current || true
            echo
            echo "HEAD commit:"
            git -C "$scripts_path/$repo" rev-parse HEAD || true
            echo
            echo "HEAD summary:"
            git -C "$scripts_path/$repo" log -1 --date=iso || true
            echo
            echo "Working tree status:"
            git -C "$scripts_path/$repo" status --short --branch || true
            echo
        fi
    done
} > "$git_report_file"

# Main human-readable metadata file
{
    echo "ENVIRONMENT METADATA"
    echo "===================="
    echo
    echo "Creation timestamps"
    echo "-------------------"
    echo "UTC:   $created_at_utc"
    echo "Local: $created_at_local"
    echo
    echo "Environment"
    echo "-----------"
    echo "Requested base prefix: $base_prefix"
    echo "Created env prefix:    $env_prefix"
    echo "Python version:"
    python --version
    echo
    echo "System"
    echo "------"
    echo "User: $(whoami)"
    echo "Hostname: $(hostname)"
    echo "Working directory: $(pwd)"
    echo "Kernel: $(uname -srmo)"
    echo
    echo "Micromamba"
    echo "----------"
    echo "Micromamba executable: $(command -v micromamba)"
    echo "Micromamba version: $(micromamba --version)"
    echo
    echo "Environment paths"
    echo "-----------------"
    echo "site-packages: $site_packages"
    echo "PyCOMPLETE scripts path: $scripts_path"
    echo
    echo "Installed package summary"
    echo "-------------------------"
    echo "micromamba list saved to:       $micromamba_list_file"
    echo "pip freeze saved to:            $pip_freeze_file"
    echo "micromamba env export saved to: $micromamba_export_file"
    echo
    echo "Git metadata"
    echo "------------"
    echo "Detailed git report saved to: $git_report_file"
    echo
    echo "Top-level cloned repositories"
    echo "-----------------------------"
    find "$scripts_path" -maxdepth 1 -mindepth 1 -type d | sort
    echo
    echo "local-packages.pth contents"
    echo "---------------------------"
    cat "$site_packages/local-packages.pth"
    echo
    echo "Activation"
    echo "----------"
    echo "micromamba activate \"$env_prefix\""
} > "$metadata_file"

cd ..

micromamba deactivate

echo "Added scripts to environment"
echo "Environment path: $env_prefix"
echo "Metadata written to: $metadata_file"
echo "Environment can be activated via activate_env.sh"

cat > activate_env.sh <<EOF
#!/usr/bin/env bash
eval "\$(micromamba shell hook --shell bash)"
micromamba activate "$env_prefix"
EOF
chmod +x ./activate_env.sh
