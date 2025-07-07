#!/bin/bash

#SBATCH --job-name=dip_0001        # Job name
#SBATCH --output=%j.out            # Standard output file (%j = job ID)
#SBATCH --error=%j.err             # Standard error file
#SBATCH --mail-type=FAIL           # Email on job end and failure
#SBATCH --mail-user=evangelos.katralis@cern.ch  
#SBATCH --partition=hpc_acc        # Queue/partition name
#SBATCH --ntasks=8                 # Total number of MPI tasks
#SBATCH --ntasks-per-node=8        # Tasks per node
#SBATCH --nodes=1                  # Number of nodes (optional, inferred from above)
#SBATCH --time 23:59:59

# Load Relevant Modules
module load mpi/openmpi-x86_64

# Extract sim class git info
PyPARIS_sim_class_folder=$(conda run -p /home/HPC/ekatrali/.conda/envs/sim_env python -c "import PyPARIS_sim_class,os; print(os.path.dirname(PyPARIS_sim_class.__file__))")

cwd=$(pwd)
cd "$PyPARIS_sim_class_folder"

echo "Version:"          >  $cwd/SimClass_git_info.txt
cat __version__.py       >> $cwd/SimClass_git_info.txt
echo " "                 >> $cwd/SimClass_git_info.txt
echo "git status:"       >> $cwd/SimClass_git_info.txt
git status               >> $cwd/SimClass_git_info.txt
echo "git log -n 1:"     >> $cwd/SimClass_git_info.txt
git log -n 1             >> $cwd/SimClass_git_info.txt

cd $cwd

# Run using python multiprocessing
conda run -p /home/HPC/ekatrali/.conda/envs/sim_env python -m PyPARIS.multiprocexec -n 8 sim_class=PyPARIS_sim_class.Simulation.Simulation >> stdout.txt 2>> stderr.txt

# Run using python multiprocessing
mpiexec -n 8 conda run -p /home/HPC/ekatrali/.conda/envs/sim_env python -m PyPARIS.withmpi sim_class=PyPARIS_sim_class.Simulation.Simulation >> stdout.txt 2>> stderr.txt