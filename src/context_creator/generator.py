import pathlib
import fnmatch
import os

class ProjectContextGenerator:
    def __init__(self, project_root, output_file_name, ignore_spec_path):
        self.root_directory = project_root.resolve()
        self.output_filepath = self.root_directory / output_file_name
        self.ignore_filepath = ignore_spec_path
        
        self.root_patterns = set()
        self.name_patterns = set()
        self._prepare_ignore_patterns(output_file_name)

    def _prepare_ignore_patterns(self, output_filename):
        base_patterns = {output_filename, ".contextignore"}
        if self.ignore_filepath and self.ignore_filepath.is_file():
            try:
                with self.ignore_filepath.open('r', encoding='utf-8') as spec_file:
                    for line in spec_file:
                        stripped_line = line.strip()
                        if stripped_line and not stripped_line.startswith('#'):
                            base_patterns.add(stripped_line)
            except IOError as e:
                print(f"Warning: Could not read ignore spec file: {e}")
        
        for pattern in base_patterns:
            if "/" in pattern.strip('/'):
                self.root_patterns.add(pattern)
            else:
                self.name_patterns.add(pattern)

    def _is_path_ignored(self, path):
        relative_path = path.relative_to(self.root_directory).as_posix()

        for pattern in self.root_patterns:
            if fnmatch.fnmatch(relative_path, pattern):
                return True

        for pattern in self.name_patterns:
            pattern_is_dir = pattern.endswith('/')
            base_pattern = pattern.rstrip('/')
            
            if fnmatch.fnmatch(path.name, base_pattern):
                if pattern_is_dir and not path.is_dir():
                    continue
                return True
        return False

    def _render_directory_tree(self, paths):
        tree_lines = []
        structure = {}
        
        for path in paths:
            parts = path.relative_to(self.root_directory).parts
            level = structure
            for part in parts:
                level = level.setdefault(part, {})
        
        def build_recursive(level, prefix=""):
            entries = sorted(level.keys())
            for i, entry in enumerate(entries):
                connector = "└── " if i == len(entries) - 1 else "├── "
                tree_lines.append(f"{prefix}{connector}{entry}")
                if level[entry]:
                    extension = "    " if i == len(entries) - 1 else "│   "
                    build_recursive(level[entry], prefix + extension)

        tree_lines.append(f"{self.root_directory.name}/")
        build_recursive(structure)
        return "\n".join(tree_lines)

    def generate_context_file(self):
        included_paths = set()
        for root, dirs, files in os.walk(self.root_directory, topdown=True):
            current_root_path = pathlib.Path(root)

            dirs[:] = [d for d in dirs if not self._is_path_ignored(current_root_path / d)]

            all_paths_in_scope = (current_root_path / p for p in dirs + files)
            for path in all_paths_in_scope:
                if not self._is_path_ignored(path):
                    included_paths.add(path)
        
        sorted_paths = sorted(list(included_paths))
        included_files = [p for p in sorted_paths if p.is_file()]
        tree_string = self._render_directory_tree([self.root_directory] + sorted_paths)

        try:
            with self.output_filepath.open('w', encoding='utf-8') as output_file:
                output_file.write(tree_string + "\n\n")

                for file_path in included_files:
                    relative_path = file_path.relative_to(self.root_directory).as_posix()
                    output_file.write(f"--- {relative_path} ---\n")

                    try:
                        with file_path.open('r', encoding='utf-8', errors='ignore') as content_file:
                            content = content_file.read()
                        
                        file_extension = file_path.suffix.lstrip('.')
                        output_file.write(f"````{file_extension}\n")
                        output_file.write(content)
                        output_file.write("\n````\n\n")
                    except Exception as e:
                        output_file.write(f"Error reading file: {e}\n\n")
            
            return self.output_filepath

        except IOError as e:
            print(f"Error: Failed to write to {self.output_filepath}: {e}")
            return None