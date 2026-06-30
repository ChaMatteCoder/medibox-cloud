# MediBox Cloud

MediBox Cloud e uma base backend academica para controle inteligente de medicamentos. O projeto simula uma caixa inteligente capaz de enviar eventos para a nuvem, enquanto cuidadores cadastram pacientes, medicamentos e horarios de uso.

O foco e demonstrar uma arquitetura backend simples, modular e explicavel usando Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT, RabbitMQ, Docker Compose, NGINX e uma base inicial para Kubernetes.

## Arquitetura

```txt
medibox-cloud/
  services/
    auth-service/
    medication-service/
    event-service/
    notification-worker/
  gateway/
  infra/
    docker/
    k8s/
  docs/
  docker-compose.yml
  .env.example
  README.md
```

## Servicos

`auth-service`

- Cadastro de usuario.
- Login com JWT.
- Endpoint `/auth/me`.
- Papeis: `ADMIN`, `CAREGIVER`, `PATIENT`.

`medication-service`

- Cadastro e consulta de pacientes.
- Cadastro e consulta de medicamentos.
- Cadastro e consulta de horarios por paciente.

`event-service`

- Registro de eventos da caixa inteligente.
- Publicacao de mensagens na fila `medibox.notifications`.

`notification-worker`

- Consome mensagens do RabbitMQ.
- Simula notificacoes por logs no terminal.

## Como rodar com Docker Compose

Na raiz do projeto:

```bash
docker compose up --build
```

O Compose usa valores padrao equivalentes aos de `.env.example`. Para um ambiente local editavel, crie um `.env` a partir do exemplo:

```bash
cp .env.example .env
```

Depois acesse:

- Gateway: http://localhost
- RabbitMQ Management: http://localhost:15672
- Usuario RabbitMQ: `medibox`
- Senha RabbitMQ: `medibox`

## Documentacao Swagger

Pelo gateway:

- Auth: http://localhost/auth/docs
- Medications: http://localhost/medications/docs
- Events: http://localhost/events/docs

Portas diretas dos servicos:

- Auth service: http://localhost:8001/docs nao e usado; use http://localhost:8001/auth/docs
- Medication service: http://localhost:8002/medications/docs
- Event service: http://localhost:8003/events/docs

## Endpoints principais

Auth:

```txt
POST /auth/register
POST /auth/login
GET  /auth/me
GET  /health
```

Medication:

```txt
POST /patients
GET  /patients
GET  /patients/{patient_id}

POST /medications
GET  /medications
GET  /medications/{medication_id}

POST /schedules
GET  /schedules/patient/{patient_id}

GET  /health
```

Events:

```txt
POST /events
GET  /events
GET  /events/patient/{patient_id}
GET  /health
```

As rotas de pacientes, medicamentos, horarios e eventos exigem Bearer Token gerado pelo `auth-service`.

## Fluxo rapido de teste

1. Cadastre um usuario:

```bash
curl -X POST http://localhost/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Ana Cuidadora\",\"email\":\"ana@example.com\",\"password\":\"123456\",\"role\":\"CAREGIVER\"}"
```

2. Faca login e copie o `access_token`:

```bash
curl -X POST http://localhost/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"ana@example.com\",\"password\":\"123456\"}"
```

3. Use o token nas demais chamadas:

```bash
curl -X GET http://localhost/patients \
  -H "Authorization: Bearer SEU_TOKEN"
```

## RabbitMQ

Quando `POST /events` cria um evento, o `event-service` publica uma mensagem na fila:

```txt
medibox.notifications
```

Exemplo de mensagem:

```json
{
  "event_id": "...",
  "patient_id": "...",
  "medication_id": "...",
  "event_type": "DOSE_MISSED",
  "occurred_at": "2026-06-30T10:00:00+00:00"
}
```

O `notification-worker` consome essa fila e registra um log semelhante a:

```txt
[NOTIFICATION] Paciente X gerou evento DOSE_MISSED. Alerta simulado enviado ao cuidador.
```

## Banco e migrations

O projeto usa PostgreSQL com um banco compartilhado para simplificar a apresentacao academica.

Cada servico com banco possui seu proprio Alembic:

- `services/auth-service/alembic`
- `services/medication-service/alembic`
- `services/event-service/alembic`

Cada um usa uma tabela de versao propria, evitando conflito no banco compartilhado.

## Kubernetes

Os manifests basicos ficam em:

```txt
infra/k8s/
```

Arquivos incluidos:

- namespace;
- ConfigMap;
- Secret de exemplo;
- PostgreSQL;
- RabbitMQ;
- deployments dos servicos;
- services internos;
- NGINX gateway;
- ingress.

Antes de aplicar em um cluster real, copie `secret.example.yaml`, ajuste os segredos e publique as imagens Docker com nomes acessiveis ao cluster.

Exemplo de aplicacao:

```bash
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/configmap.yaml
kubectl apply -f infra/k8s/secret.example.yaml
kubectl apply -f infra/k8s/
```

## Proximos passos possiveis

- Adicionar testes automatizados por servico.
- Criar endpoints para solicitacao de mudanca de horario pelo paciente.
- Adicionar autorizacao por papel em rotas sensiveis.
- Melhorar observabilidade com logs estruturados.
- Separar bancos por servico em uma evolucao da arquitetura.
- Criar pipeline CI/CD.
- Evoluir os manifests Kubernetes para Helm quando fizer sentido.
