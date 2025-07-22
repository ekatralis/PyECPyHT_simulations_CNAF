alias view_jobs='squeue -u $USER'

alias home='cd ~'

alias copy_to_eos='/path/to/copy_to_eos'

sims() {
    SIMS_DIR_FILE="$HOME/.sims_dir"

    if [[ "$1" == "--set_dir" ]]; then
        if [[ -z "$2" ]]; then
            echo "$PWD" > "$SIMS_DIR_FILE"
            echo "Simulation directory set to current directory: $PWD"
        else
            if [[ -d "$2" ]]; then
                echo "$2" > "$SIMS_DIR_FILE"
                echo "Simulation directory set to: $2"
            else
                echo "Error: Directory '$2' does not exist."
                return 1
            fi
        fi
    else
        if [[ -f "$SIMS_DIR_FILE" ]]; then
            SIM_DIR=$(cat "$SIMS_DIR_FILE")
            if [[ -d "$SIM_DIR" ]]; then
                cd "$SIM_DIR" || return
                echo "Changed to simulation directory: $SIM_DIR"
            else
                echo "Error: Saved simulation directory '$SIM_DIR' does not exist."
                return 1
            fi
        else
            echo "No simulation directory set. Use 'sims --set_dir' to set one."
            return 1
        fi
    fi
}