import os
import shutil
import numpy as np
from replaceline import replaceline_and_save
import argparse

parser = argparse.ArgumentParser(prog = "PyPARIS config scan to scan")
parser.add_argument("--ref_sim", help="Select path to reference simulation", type = str, required=True)
parser.add_argument("--sim_dir", help="Select directory for simulation output", type = str, required=True)
parser.add_argument("--multithreading_mode", type = str, default = "MPI", choices=["MPI", "Multiproc"])
parser.add_argument("--n_cores", help = "Number of cores to request", type = int, default = 8)
parser.add_argument("--job_prefix", help = "Prefix for job", type = str, default = "eldens_")
parser.add_argument("--fail_email", type = str, help = "Email to send notice in case of failuer", required = True)
parser.add_argument("--conda_env", type = str, help = "Path to conda environment", required = True)
parser.add_argument("--queue_name", type = str, help = "Name of the queue to submit the jobs to", required = True)
parser.add_argument("--use_conda_run", action="store_true", help="Use conda run command in launch file as opposed to activating environment")
args = parser.parse_args()

ref_sim = os.path.abspath(args.ref_sim)
output_dir = os.path.abspath(args.sim_dir)
os.makedirs(output_dir,exist_ok=True)
job_prefix = args.job_prefix
fail_email = args.fail_email
n_cores = args.n_cores
conda_env_path = args.conda_env
queue_name = args.queue_name
use_conda_run = args.use_conda_run
sim_submit_file = os.path.join(output_dir, "launch_sims.sh")
# Scan electron density
el_densities = np.concatenate([np.array([1e10,1e11,5e11]),np.arange(1e12, 1e13,1e12),np.arange(1e13, 5e13,1e13)],axis = 0)

if os.path.exists(sim_submit_file):
    os.remove(sim_submit_file)

for el_dens in el_densities:
    job_name = job_prefix+f"{el_dens:.2e}"
    sim_dir = os.path.join(output_dir, job_name)
    job_header = f"""#!/bin/bash
#SBATCH --job-name={job_name}        # Job name
#SBATCH --output=%j.out            # Standard output file (%j = job ID)
#SBATCH --error=%j.err             # Standard error file
#SBATCH --mail-type=FAIL           # Email on job end and failure
#SBATCH --mail-user={fail_email} 
#SBATCH --partition={queue_name}        # Queue/partition name
#SBATCH --ntasks={n_cores}                 # Total number of MPI tasks
#SBATCH --ntasks-per-node=8        # Tasks per node
#SBATCH --nodes=1                  # Number of nodes (optional, inferred from above)
#SBATCH --chdir={sim_dir}
#SBATCH --time 23:59:59
# """

    module_import = ""
    conda_run_cmd = ""
    activate_env = ""
    if not use_conda_run:
        activate_env = f"""
eval "$(conda shell.bash hook)"
conda activate {conda_env_path}
"""
    else:
        conda_run_cmd = f"conda run -p {conda_env_path}"
    if args.multithreading_mode == "MPI":
        module_import = "module load mpi/openmpi-x86_64"
        launch_cmd = f"stdbuf -oL mpiexec -n {n_cores} {conda_run_cmd} python -m PyPARIS.withmpi sim_class=PyPARIS_sim_class.Simulation.Simulation >> stdout.txt 2>> stderr.txt"
    elif args.multithreading_mode == "Multiproc":
        module_import = ""
        launch_cmd = f"stdbuf -oL {conda_run_cmd} python -m PyPARIS.multiprocexec -n {n_cores} sim_class=PyPARIS_sim_class.Simulation.Simulation >> stdout.txt 2>> stderr.txt"

    shutil.copytree(ref_sim, sim_dir)

    replaceline_and_save(os.path.join(sim_dir,"Simulation_parameters.py"),"init_unif_edens_dip =", f"init_unif_edens_dip = {el_dens:.5e}")
    
    job_file = os.path.join(sim_dir,"job.cmd")
    with open(job_file, "w") as f:
        f.write(job_header+"\n\n")
        # f.write(f"cd {sim_dir}\n\n")
        f.write(module_import+"\n")
        f.write(activate_env+"\n")
        f.write(launch_cmd)
    
    with open(sim_submit_file, "a") as f:
        f.write(f"sbatch {job_file}\n")
    