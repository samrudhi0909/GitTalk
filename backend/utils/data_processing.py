import os
import shutil
import stat
import git

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clone_repo(repo_url):
    repo_dir = os.path.join(os.getcwd(), 'cloned_repo')
    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir, onerror=remove_readonly)
    git.Repo.clone_from(repo_url, repo_dir, depth=1)
    return repo_dir

def read_code_files(repo_dir):
    file_extensions = ['.py', '.js', '.java', '.c', '.cpp', '.txt', '.md']
    code_contents = []
    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if d != '.git']
        for file in files:
            if any(file.lower().endswith(ext) for ext in file_extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        code_contents.append(content)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    return code_contents