# Dispatcher FD Test Files

This repository hosts configuration files and scripts used to compare **file descriptor (FD) usage** in the Ansible Dispatcher when using **fork** vs. **forkserver**.

## 📂 Files  
- **Test Scripts:**
  - `compare_fd.sh` – Runs dispatcher in both modes and collects FD stats.
  - `submit_many_tasks.py` – Submits test tasks to the dispatcher.
  - `pid-host-to-container.py` – Extracts open FD counts from dispatcher processes.

- **Configuration Files:**
  - `config_fork.yml` – Uses `ProcessManager` (fork).
  - `config_forkserver.yml` – Uses `ForkServerManager` (forkserver).

## 📌 Purpose  
These files were used to validate that **forkserver significantly reduces file descriptor usage per worker**, confirming the proposed fix.
