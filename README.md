# DevOps CLI

AI-powered Kubernetes resource generator.

## Installation

```bash
pip install .
```

## Requirements

- Python 3.9+
- OpenAI API Key (`export OPENAI_API_KEY=sk-...`)
- `kubeconform` (for validation)

### Installing kubeconform
**Mac:**
```bash
brew install kubeconform
```

## Usage

```bash
devops-cli k8s generate --prompt "nginx deployment with 2 replicas" --env prod
```
