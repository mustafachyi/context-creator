import argparse
import pathlib
import sys
from .generator import ProjectContextGenerator

DEFAULT_IGNORE_CONTENT = """.contextignore
context.txt

.git/
.svn/
.hg/
.github/

.idea/
.vscode/
.DS_Store
Thumbs.db

.env
*.env.*
!.env.example
secrets.*
credentials.*
*.pem
*.key

node_modules/
vendor/
dist/
build/
public/
coverage/

__pycache__/
venv/
env/
*.pyc
.pytest_cache/
.tox/

package-lock.json
yarn.lock
bun.lock
npm-debug.log*
yarn-error.log

target/
*.class
*.jar
*.war

bin/
obj/

.bundle/
log/
tmp/

.terraform/
.terraform.lock.hcl
*.tfstate
*.tfstate.*

*.log
*.zip
*.tar.gz
*.rar
*.so
*.o
*.dll
*.exe
"""

def main():
    parser = argparse.ArgumentParser(
        description="Generate a single context file from a project directory.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "project_directory",
        type=pathlib.Path,
        nargs='?',
        default=pathlib.Path.cwd(),
        help="The root directory of the project (default: current directory)."
    )
    parser.add_argument(
        "-o", "--output",
        default="context.txt",
        help="The name of the output file (default: context.txt)."
    )

    args = parser.parse_args()
    project_dir = args.project_directory.resolve()

    if not project_dir.is_dir():
        print(f"Error: Project directory not found at '{project_dir}'")
        sys.exit(1)

    ignore_file_path = project_dir / ".contextignore"

    if not ignore_file_path.is_file():
        print("Created default .contextignore file.")
        try:
            with ignore_file_path.open('w', encoding='utf-8') as f:
                f.write(DEFAULT_IGNORE_CONTENT)
        except IOError as e:
            print(f"Error: Could not create .contextignore file: {e}")
            sys.exit(1)

    generator = ProjectContextGenerator(
        project_root=project_dir,
        output_file_name=args.output,
        ignore_spec_path=ignore_file_path
    )
    
    output_path = generator.generate_context_file()
    
    if output_path:
        print(f"Generated {output_path.name}.")

if __name__ == "__main__":
    main()