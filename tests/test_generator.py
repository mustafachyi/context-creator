import pathlib
import tempfile

from context_creator.generator import ProjectContextGenerator

def test_generation_with_ignore_rules():
    with tempfile.TemporaryDirectory() as temp_dir_str:
        project_root = pathlib.Path(temp_dir_str)

        (project_root / "src").mkdir()
        (project_root / "src" / "main.py").write_text("print('hello')")
        (project_root / "data").mkdir()
        (project_root / "data" / "secret.env").write_text("API_KEY=123")
        (project_root / "docs").mkdir()
        (project_root / "docs" / "manual.pdf").write_text("PDF_CONTENT")
        (project_root / ".contextignore").write_text("*.env\ndocs/\n")

        output_file_name = "output.txt"
        ignore_spec_path = project_root / ".contextignore"

        generator = ProjectContextGenerator(
            project_root=project_root,
            output_file_name=output_file_name,
            ignore_spec_path=ignore_spec_path
        )
        
        output_path = generator.generate_context_file()
        
        assert output_path is not None
        assert output_path.is_file()

        content = output_path.read_text()
        
        assert "main.py" in content
        assert "print('hello')" in content
        
        assert "secret.env" not in content
        assert "API_KEY=123" not in content

        assert "manual.pdf" not in content

def test_nested_ignore_patterns():
    with tempfile.TemporaryDirectory() as temp_dir_str:
        project_root = pathlib.Path(temp_dir_str)

        (project_root / "src").mkdir()
        (project_root / "src" / "main.py").write_text("print('main')")
        (project_root / "src" / "__pycache__").mkdir()
        (project_root / "src" / "__pycache__" / "cache.bin").write_text("CACHED")
        
        (project_root / ".contextignore").write_text("__pycache__/\n")

        output_file_name = "output.txt"
        ignore_spec_path = project_root / ".contextignore"

        generator = ProjectContextGenerator(
            project_root=project_root,
            output_file_name=output_file_name,
            ignore_spec_path=ignore_spec_path
        )
        
        output_path = generator.generate_context_file()
        
        assert output_path is not None
        
        content = output_path.read_text()

        assert "main.py" in content
        assert "__pycache__" not in content
        assert "cache.bin" not in content