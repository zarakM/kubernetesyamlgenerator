import json
from devops_cli.models.internal import GenerationRequest
from devops_cli.models.k8s import K8sResourceList
from devops_cli.llm_client import LLMClient

SYSTEM_PROMPT = """
You are an expert Kubernetes Helper.
Your task is to generate Kubernetes YAML resources based on the user's request.
You MUST respond with a valid JSON object that matches the following structure:
{
  "resources": [
    {
      "apiVersion": "...",
      "kind": "...",
      "metadata": { "name": "...", "labels": {...} },
      "spec": { ... },
      "data": { ... } // for ConfigMap
    }
  ]
}

Ensure you follow these best practices:
1. Always include 'resources' (requests and limits) for containers.
2. Always include livenessProbe and readinessProbe for Deployments.
3. Do NOT use 'latest' tag for images unless specified; default to 'latest' only if unknown, but prefer specific versions if implied.
4. Do NOT include privileged security contexts.
5. Add standard labels: app, environment.
6. For Service, default to ClusterIP unless asked otherwise.
"""

class K8sGenerator:
    def __init__(self):
        self.llm_client = LLMClient()

    def generate(self, request: GenerationRequest) -> K8sResourceList:
        user_prompt = f"""
        Request: {request.prompt}
        Environment: {request.environment}
        Replicas: {request.replicas}
        Namespace: {request.namespace}
        Expose Service: {request.expose} (Type: {request.expose_type})
        
        Generate the necessary Kubernetes resources (Deployment, Service, ConfigMap, etc.).
        """
        
        raw_response = self.llm_client.generate_resources(SYSTEM_PROMPT, user_prompt)
        
        # Validate with Pydantic
        try:
            validated_resources = K8sResourceList.model_validate(raw_response)
            return validated_resources
        except Exception as e:
            print("Failed to validate response against Pydantic models.")
            print(f"Raw response: {json.dumps(raw_response, indent=2)}")
            raise e
