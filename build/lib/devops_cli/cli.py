import typer
import os
import sys
from rich.console import Console
from rich.panel import Panel
from typing import Optional
from devops_cli.models.internal import GenerationRequest
from devops_cli.generators.k8s_generator import K8sGenerator
from devops_cli.renderers.yaml_renderer import YamlRenderer
from devops_cli.validators.k8s_validator import K8sValidator

app = typer.Typer(help="AI-powered DevOps CLI")
k8s_app = typer.Typer(help="Kubernetes management commands")
app.add_typer(k8s_app, name="k8s")
console = Console()

@k8s_app.command()
def generate(
    prompt: str = typer.Option(..., "--prompt", "-p", help="Description of the Kubernetes resources to generate"),
    output: str = typer.Option("./k8s", "--output", "-o", help="Output directory"),
    env: str = typer.Option("dev", "--env", "-e", help="Target environment"),
    replicas: int = typer.Option(1, help="Number of replicas for deployments"),
    namespace: str = typer.Option("default", "-n", help="Namespace"),
    expose: bool = typer.Option(False, help="Whether to expose deployments via Service"),
    expose_type: str = typer.Option("ClusterIP", help="Service type if exposed (ClusterIP, NodePort, LoadBalancer)")
):
    """
    Generate Kubernetes manifests using AI.
    """
    console.print(Panel(f"Generating resources for: [bold]{prompt}[/bold]", title="DevOps CLI"))

    # 1. Build Request
    req = GenerationRequest(
        prompt=prompt,
        environment=env,
        namespace=namespace,
        replicas=replicas,
        expose=expose,
        expose_type=expose_type
    )

    # 2. Generator (LLM)
    try:
        generator = K8sGenerator()
        console.print("[yellow]Wait... Contacting OpenAI...[/yellow]")
        resources = generator.generate(req)
        console.print(f"[green]Successfully generated {len(resources.resources)} resources![/green]")
    except Exception as e:
        console.print(f"[red]Error generating resources:[/red] {e}")
        # In a real app we might want to check for OPENAI_API_KEY specifically
        if "OPENAI_API_KEY" not in os.environ:
             console.print("[bold red]Tip:[/bold red] Make sure OPENAI_API_KEY is set.")
        raise typer.Exit(code=1)

    # 3. Render
    try:
        renderer = YamlRenderer()
        files = renderer.render(resources, output)
        console.print(f"Written {len(files)} files to [bold]{output}[/bold]")
        for f in files:
            console.print(f" - {f}")
    except Exception as e:
        console.print(f"[red]Error writing files:[/red] {e}")
        raise typer.Exit(code=1)

    # 4. Validate
    validator = K8sValidator()
    console.print("\n[bold]Running Validation (kubeconform)...[/bold]")
    res = validator.validate(output)
    
    if res.valid:
        console.print("[green]Validation Passed![/green]")
    else:
        console.print("[red]Validation Failed![/red]")
        for err in res.errors:
            console.print(err)
        console.print("[yellow]Note: Validation failure doesn't delete the files. Check output dir.[/yellow]")

    console.print(Panel("Done!", style="green"))

if __name__ == "__main__":
    app()
