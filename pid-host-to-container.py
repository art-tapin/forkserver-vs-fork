import psutil
import re
import os
import argparse

# Function to get PIDs matching a regex based on the full command line
def get_pids_by_cmdline_regex(cmdline_regex):
    pids = []
    pattern = re.compile(cmdline_regex)
    
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            # Match the full command line using the regex
            if proc.info['cmdline'] and pattern.search(' '.join(proc.info['cmdline'])):
                pids.append(proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return pids

# Function to read NSpid from /proc/{pid}/status
def get_nspid_for_process(pid):
    try:
        # Open the /proc/{pid}/status file to extract the NSpid
        with open(f"/proc/{pid}/status", 'r') as f:
            for line in f:
                if line.startswith("NSpid"):
                    # Extract the NSpid value, which is a list of process IDs in the container's namespace
                    nspid = line.strip().split("\t")[1]
                    return nspid
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error reading /proc/{pid}/status: {e}")
        return None

# Function to get the number of open file descriptors for a process
def get_num_open_fds(pid):
    try:
        proc = psutil.Process(pid)
        # Returns the list of open files
        open_files = proc.open_files()
        return len(open_files)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None

def get_open_files_via_proc(pid):
    fd_dir = f"/proc/{pid}/fd"
    try:
        open_files = os.listdir(fd_dir)
        # Optionally resolve the symbolic links to file paths
        resolved_files = [os.readlink(os.path.join(fd_dir, fd)) for fd in open_files]
        return resolved_files
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error reading /proc/{pid}/fd: {e}")
        return []

def get_num_open_files_via_proc(pid):
    return len(get_open_files_via_proc(pid))

# Function to get container PIDs and the number of open file descriptors for processes matching cmdline regex
def get_container_pids_and_fds_by_cmdline_regex(cmdline_regex):
    # Step 1: Get matching PIDs based on full command line
    pids = get_pids_by_cmdline_regex(cmdline_regex)
    print(f"Matching PIDs: {pids}")
    
    # Step 2: Translate PIDs to container PIDs using NSpid and get the number of open FDs
    container_pids_and_fds = []
    for pid in pids:
        nspid = get_nspid_for_process(pid)
        num_fds = get_num_open_files_via_proc(pid)
        
        if nspid and num_fds is not None:
            container_pids_and_fds.append((nspid, num_fds))
    
    return container_pids_and_fds

# Command-line argument parsing
def parse_args():
    parser = argparse.ArgumentParser(description="Get container PIDs and file descriptor counts for processes matching a cmdline regex")
    parser.add_argument("cmdline_regex", help="Regex to match the full command line of processes")
    return parser.parse_args()

# Main execution
if __name__ == "__main__":
    args = parse_args()
    cmdline_regex = args.cmdline_regex
    
    # Get container PIDs and the number of open FDs for processes matching the cmdline regex pattern
    container_pids_and_fds = get_container_pids_and_fds_by_cmdline_regex(cmdline_regex)

    # Output the results
    for nspid, num_fds in container_pids_and_fds:
        print(f"Container PID: {nspid}, Open File Descriptors: {num_fds}")


