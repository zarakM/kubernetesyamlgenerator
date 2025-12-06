from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, field_validator

class K8sMetadata(BaseModel):
    name: str = Field(..., description="Name of the resource")
    namespace: str = Field("default", description="Namespace of the resource")
    labels: Dict[str, str] = Field(default_factory=dict, description="Labels for the resource")
    annotations: Optional[Dict[str, str]] = Field(default_factory=dict, description="Annotations for the resource")

class ContainerResourceRequest(BaseModel):
    cpu: str = Field("100m", description="CPU request")
    memory: str = Field("128Mi", description="Memory request")

class ContainerResourceLimit(BaseModel):
    cpu: str = Field("500m", description="CPU limit")
    memory: str = Field("512Mi", description="Memory limit")

class ContainerResources(BaseModel):
    requests: ContainerResourceRequest = Field(default_factory=ContainerResourceRequest)
    limits: ContainerResourceLimit = Field(default_factory=ContainerResourceLimit)

class ContainerPort(BaseModel):
    containerPort: int = Field(..., description="Port exposed by the container")
    protocol: str = Field("TCP", description="Protocol (TCP/UDP)")

class ContainerProbe(BaseModel):
    httpGet: Optional[Dict[str, Any]] = None
    tcpSocket: Optional[Dict[str, Any]] = None
    exec: Optional[Dict[str, Any]] = None # 'exec' is a keyword in python, but valid in k8s yaml, handled by alias or dict export
    initialDelaySeconds: int = 10
    periodSeconds: int = 10

class Container(BaseModel):
    name: str
    image: str
    imagePullPolicy: str = "IfNotPresent"
    ports: List[ContainerPort] = Field(default_factory=list)
    resources: ContainerResources = Field(default_factory=ContainerResources)
    env: List[Dict[str, str]] = Field(default_factory=list)
    readinessProbe: Optional[ContainerProbe] = None
    livenessProbe: Optional[ContainerProbe] = None
    securityContext: Dict[str, Any] = Field(default={"allowPrivilegeEscalation": False}, description="Container security context")

class PodSpec(BaseModel):
    containers: List[Container]
    restartPolicy: str = "Always"
    serviceAccountName: Optional[str] = None
    securityContext: Dict[str, Any] = Field(default={}, description="Pod security context")

class DeploymentSpec(BaseModel):
    replicas: int = Field(1, ge=1)
    selector: Dict[str, Dict[str, str]] = Field(description="Label selector")
    template: Dict[str, Any] = Field(description="Pod template")

    @field_validator('template')
    @classmethod
    def validate_template(cls, v):
        # In a real scenario we'd unpack this further, but for simplicity keeping it flexible
        # or mapping to a PodTemplateSpec model
        return v

# More strict Deployment model
class K8sDeployment(BaseModel):
    apiVersion: str = "apps/v1"
    kind: str = "Deployment"
    metadata: K8sMetadata
    spec: Any  # keeping it loosely typed to match K8s flexibility or strictly typed if we define DeploymentSpec fully

class ServicePort(BaseModel):
    port: int
    targetPort: Union[int, str]
    protocol: str = "TCP"
    name: Optional[str] = None

class ServiceSpec(BaseModel):
    selector: Dict[str, str]
    ports: List[ServicePort]
    type: str = "ClusterIP"

class K8sService(BaseModel):
    apiVersion: str = "v1"
    kind: str = "Service"
    metadata: K8sMetadata
    spec: ServiceSpec

class K8sConfigMap(BaseModel):
    apiVersion: str = "v1"
    kind: str = "ConfigMap"
    metadata: K8sMetadata
    data: Dict[str, str] = Field(default_factory=dict)

# Union type for list of resources
class K8sResourceList(BaseModel):
    resources: List[Union[K8sDeployment, K8sService, K8sConfigMap, Dict[str, Any]]]
