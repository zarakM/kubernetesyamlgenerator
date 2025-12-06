import shutil
import subprocess
import os
from tempfile import NamedTemporaryFile
from devops_cli.models.internal import ValidationResult

class K8sValidator:
    def __init__(self):
        self.kubeconform_path = shutil.which("kubeconform")

    def validate(self, directory: str) -> ValidationResult:
        if not self.kubeconform_path:
            return ValidationResult(
                valid=False,
                errors=["kubeconform binary not found in PATH. Please install it to enable validation."]
            )

        # Run kubeconform on the directory
        # -summary: print summary
        # -output json: easier to parse if needed, but text is fine for CLI output usually.
        # Let's stick to text capture for simplicity or simple exit code check.
        
        try:
            result = subprocess.run(
                [self.kubeconform_path, "-summary", "-ignore-missing-schemas", directory],
                capture_output=True,
                text=True
            )
            
            valid = (result.returncode == 0)
            errors = []
            if not valid:
                errors = result.stderr.splitlines() + result.stdout.splitlines()
            
            # Count resources (naive count based on files in dir for now or parsing summary)
            # Simplest for now is just return status
            
            return ValidationResult(
                valid=valid,
                errors=errors
            )

        except Exception as e:
            return ValidationResult(valid=False, errors=[str(e)])
