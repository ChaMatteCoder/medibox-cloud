# Validação Kubernetes Local com Kind

Este guia mostra como validar a MediBox Cloud em um cluster Kubernetes local usando Kind. Ele não substitui o Docker Compose; é apenas uma forma de testar a organização dos manifests em `infra/k8s/`.

## 1. Instalar Kind no Windows

Opções comuns:

```powershell
winget install Kubernetes.kind
```

Ou, usando Chocolatey:

```powershell
choco install kind
```

Depois confirme:

```powershell
kind version
kubectl version --client
docker info
```

## 2. Criar o Cluster

```powershell
kind create cluster --name medibox
```

O contexto esperado no `kubectl` será:

```txt
kind-medibox
```

Valide:

```powershell
kubectl config current-context
kubectl cluster-info
kubectl get nodes
```

## 3. Construir as Imagens Locais

A partir da raiz do projeto:

```powershell
docker build -t medibox-auth-service:local services/auth-service
docker build -t medibox-medication-service:local services/medication-service
docker build -t medibox-event-service:local services/event-service
docker build -t medibox-notification-worker:local services/notification-worker
```

As tags acima precisam bater com as imagens nos manifests:

```txt
medibox-auth-service:local
medibox-medication-service:local
medibox-event-service:local
medibox-notification-worker:local
```

## 4. Carregar Imagens no Kind

```powershell
kind load docker-image medibox-auth-service:local --name medibox
kind load docker-image medibox-medication-service:local --name medibox
kind load docker-image medibox-event-service:local --name medibox
kind load docker-image medibox-notification-worker:local --name medibox
```

## 5. Validar Manifests

Com cluster ativo:

```powershell
kubectl apply --dry-run=client -f infra/k8s/
```

Validação YAML local, sem depender do cluster:

```powershell
python -c "import yaml, pathlib; files=list(pathlib.Path('infra/k8s').glob('*.yaml')); [list(yaml.safe_load_all(p.read_text())) for p in files]; print(f'YAML OK: {len(files)} files')"
```

## 6. Aplicar Manifests

Para aplicar tudo de forma simples:

```powershell
kubectl apply -f infra/k8s/
```

Ou de forma didática:

```powershell
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/configmap.yaml
kubectl apply -f infra/k8s/secret.example.yaml
kubectl apply -f infra/k8s/postgres-deployment.yaml
kubectl apply -f infra/k8s/postgres-service.yaml
kubectl apply -f infra/k8s/rabbitmq-deployment.yaml
kubectl apply -f infra/k8s/rabbitmq-service.yaml
kubectl apply -f infra/k8s/auth-deployment.yaml
kubectl apply -f infra/k8s/auth-service.yaml
kubectl apply -f infra/k8s/medication-deployment.yaml
kubectl apply -f infra/k8s/medication-service.yaml
kubectl apply -f infra/k8s/event-deployment.yaml
kubectl apply -f infra/k8s/event-service.yaml
kubectl apply -f infra/k8s/notification-worker-deployment.yaml
kubectl apply -f infra/k8s/gateway-deployment.yaml
kubectl apply -f infra/k8s/gateway-service.yaml
kubectl apply -f infra/k8s/ingress.yaml
```

## 7. Verificar Recursos

```powershell
kubectl get namespace medibox
kubectl get pods -n medibox
kubectl get services -n medibox
kubectl get ingress -n medibox
kubectl get deployments -n medibox
```

Para acompanhar a subida:

```powershell
kubectl get pods -n medibox -w
```

## 8. Acessar o Gateway por Port-Forward

```powershell
kubectl port-forward -n medibox service/gateway-service 8080:80
```

Em outro terminal:

```powershell
curl http://localhost:8080/health
curl http://localhost:8080/auth/docs
curl http://localhost:8080/medications/docs
curl http://localhost:8080/events/docs
```

## 9. Consultar Logs

Serviços FastAPI:

```powershell
kubectl logs -n medibox deployment/auth-service
kubectl logs -n medibox deployment/medication-service
kubectl logs -n medibox deployment/event-service
```

Worker:

```powershell
kubectl logs -n medibox deployment/notification-worker
```

Gateway:

```powershell
kubectl logs -n medibox deployment/nginx-gateway
```

RabbitMQ e PostgreSQL:

```powershell
kubectl logs -n medibox deployment/rabbitmq
kubectl logs -n medibox deployment/postgres
```

## 10. Remover Recursos ou Cluster

Remover apenas os recursos da aplicação:

```powershell
kubectl delete -f infra/k8s/
```

Remover o cluster Kind inteiro:

```powershell
kind delete cluster --name medibox
```

## Observações

- O Ingress está presente para demonstrar a arquitetura, mas no Kind pode exigir um Ingress Controller adicional para uso real.
- Para validação simples, prefira `kubectl port-forward` no `gateway-service`.
- O arquivo `secret.example.yaml` é didático. Em ambiente real, substitua os valores antes de aplicar.
