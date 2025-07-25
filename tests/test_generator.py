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
        
        output_path = generator.generate()
        
        assert output_path is not None, "Generator failed to produce an output path."
        assert output_path.is_file(), "Output file was not created."

        content = output_path.read_text()
        
        assert "main.py" in content, "Included file 'main.py' is missing from output."
        assert "print('hello')" in content, "Content of 'main.py' is missing."
        
        assert "secret.env" not in content, "Ignored file 'secret.env' was incorrectly included."
        assert "API_KEY=123" not in content, "Content of ignored file was incorrectly included."

        assert "manual.pdf" not in content, "File in ignored directory 'docs/' was incorrectly included."