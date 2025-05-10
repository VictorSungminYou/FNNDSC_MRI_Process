import subprocess
import os
from multiprocessing import Pool, Manager
import argparse

def run_script(args):
    """Runs the main.py script with the given data path as an argument and updates progress."""
    data_path, progress = args
    # python3 /neuro/users/mri.team/Codes/pipeline_2024/part2/main.py --iSEGM ${file}/recon_segmentation/segmentation_to31_final.nii --outdir ${file}/surfaces
    command = ["python3", "/neuro/users/mri.team/Codes/pipeline_2024/part2/main.py", "--iSEGM", '{}/recon_segmentation/segmentation_to31_final.nii'.format(data_path), '--outdir', '{}/surfaces'.format(data_path)]
    try:
        subprocess.run(command, check=True, text=True, capture_output=True)
        progress["count"] += 1
        total = progress["total"]
        count = progress["count"]
        progress_bar = f"[{int(count / total * 50) * '='}{(50 - int(count / total * 50)) * ' '}]"
        print(f"{progress_bar} {count}/{total} processed", end="\r")
    except subprocess.CalledProcessError as e:
        print(f"\n[Info] Error while processing {data_path}: {e.stderr}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run main.py in parallel for multiple data paths.")
    parser.add_argument("data_paths", nargs='+', help="List of data paths to process")
    args = parser.parse_args()

    # List of data paths to process
    data_paths = args.data_paths

    # Number of processes to run in parallel
    num_processes = min(len(data_paths), os.cpu_count())  # Adjust based on CPU cores available

    print("[Info] Data paths to process:")
    for path in data_paths:
        print(f"- {path}")

    print(f"\n[Info] Starting processing with {num_processes} processes...")  # Print message before starting

    with Manager() as manager:
        progress = manager.dict()
        progress["count"] = 0
        progress["total"] = len(data_paths)

        with Pool(processes=num_processes) as pool:
            pool.map(run_script, [(data_path, progress) for data_path in data_paths])

    print("\n[Info] All tasks completed.")  # Print message after all tasks are done
