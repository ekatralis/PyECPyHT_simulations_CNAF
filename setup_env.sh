#!/usr/bin/env bash

base_name="sim_env"
env_name=$base_name
counter=1

# Check if conda environment exists
env_exists() {
    conda env list | awk '{print $1}' | grep -xq "$1"
}

# Get path to conda environment
get_env_path() {
    conda env list | awk '$1 == "'"$1"'" {print $NF}'
}

# Increment env name until an unused one is found
while env_exists "$env_name"; do
    env_name="${base_name}${counter}"
    ((counter++))
done

# Create the conda environment
conda create --name "$env_name" python=3.11 -y

echo "Created conda environment: $env_name"
env_path=$(get_env_path "$env_name")
echo "Environment path: $env_path"

echo "Installing packages..."

eval "$(conda shell.bash hook)"
conda activate "$env_path"

conda install compilers meson
pip install numpy scipy matplotlib h5py cython ipython

echo "Downloading scripts..."

mkdir ./PyCOMPLETE
cd ./PyCOMPLETE
scripts_path=$(pwd)

git clone https://github.com/pycomplete/PyECLOUD
git clone https://github.com/pycomplete/PyPIC
git clone https://github.com/pycomplete/PyKLU
git clone https://github.com/pycomplete/PyHEADTAIL
git clone https://github.com/pycomplete/NAFFlib
git clone https://github.com/pycomplete/PyPARIS
git clone https://github.com/pycomplete/PyPARIS_sim_class
git clone https://github.com/pycomplete/PyPARIS_CoupledBunch_sim_class

cd PyECLOUD
./setup_pyecloud
cd ..

cd PyPIC
make
cd ..

cd PyKLU
./install
cd ..

cd PyHEADTAIL
sed -i 's/\bf2py3\b/f2py/g' Makefile
make
cd ..

cd NAFFlib/NAFFlib
make py3
cd ../../..

conda deactivate

cat <<EOF > $env_path/lib/python3.11/site-packages/local-packages.pth
$scripts_path
$scripts_path/PyHEADTAIL
$scripts_path/NAFFlib
EOF

cat $env_path/lib/python3.11/site-packages/local-packages.pth

echo "Added scripts to environment"
echo "Environment path: $env_path"
echo "Environment can be activated via activate_env.sh"
echo "conda activate $env_path" > activate_env.sh
chmod +x ./activate_env.sh