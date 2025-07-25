import pathlib
import fnmatch
import os

class ProjectContextGenerator:
    def __init__(self, project_root, output_file_name, ignore_spec_path):
        self.project_root = project_root.resolve()
        self.output_path = self.project_root / output_file_name
        self.ignore_spec_path = ignore_spec_path
        self.ignore_patterns = self._load_ignore_patterns(output_file_name)

    def _load_ignore_patterns(self, output_file_name):
        patterns = {output_file_name}
        if self.ignore_spec_path and self.ignore_spec_path.is_file():
            try:
                with self.ignore_spec_path.open('r', encoding='utf-8') as spec_file:
                    for line in spec_file:
                        stripped_line = line.strip()
                        if stripped_line and not stripped_line.startswith('#'):
                            patterns.add(stripped_line)
            except IOError as e:
                print(f"Warning: Could not read ignore spec file: {e}")
        return patterns

    def _is_path_ignored(self, path):
        relative_path_str = path.relative_to(self.project_root).as_posix()
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(relative_path_str, pattern):
                return True
            if fnmatch.fnmatch(path.name, pattern):
                return True
            if path.is_dir() and fnmatch.fnmatch(f"{relative_path_str}/", pattern):
                return True
        return False

    def _build_directory_tree_string(self, included_paths):
        tree_lines = []
        structure = {}
        
        for path in included_paths:
            parts = path.relative_to(self.project_root).parts
            current_level = structure
            for part in parts:
                current_level = current_level.setdefault(part, {})
        
        def build_recursive(structure_level, prefix=""):
            entries = sorted(structure_level.keys())
            for i, entry in enumerate(entries):
                connector = "└── " if i == len(entries) - 1 else "├── "
                tree_lines.append(f"{prefix}{connector}{entry}")
                if structure_level[entry]:
                    extension = "    " if i == len(entries) - 1 else "│   "
                    build_recursive(structure_level[entry], prefix + extension)

        tree_lines.append(f"{self.project_root.name}/")
        build_recursive(structure)
        return "\n".join(tree_lines)

    def generate(self):
        included_files = []
        included_dirs = {self.project_root}

        for root, dirs, files in os.walk(self.project_root, topdown=True):
            current_root_path = pathlib.Path(root)
            if self._is_path_ignored(current_root_path):
                dirs[:] = []
                continue
            
            dirs[:] = [d for d in dirs if not self._is_path_ignored(current_root_path / d)]
            
            for dir_name in dirs:
                included_dirs.add(current_root_path / dir_name)

            for file_name in files:
                file_path = current_root_path / file_name
                if not self._is_path_ignored(file_path):
                    included_files.append(file_path)
        
        all_included_paths = sorted(included_dirs | set(included_files))
        tree_string = self._build_directory_tree_string(all_included_paths)

        try:
            with self.output_path.open('w', encoding='utf-8') as output_file:
                output_file.write(tree_string + "\n\n")

                for file_path in sorted(included_files):
                    relative_path = file_path.relative_to(self.project_root).as_posix()
                    output_file.write(f"--- {relative_path} ---\n")

                    try:
                        with file_path.open('r', encoding='utf-8', errors='ignore') as content_file:
                            content = content_file.read()
                        
                        file_extension = file_path.suffix.lstrip('.')
                        output_file.write(f"```{file_extension}\n")
                        output_file.write(content)
                        output_file.write("\n```\n\n")
                    except Exception as e:
                        output_file.write(f"Error reading file: {e}\n\n")
            
            return self.output_path

        except IOError as e:
            print(f"Error: Failed to write to {self.output_path}: {e}")
            return None