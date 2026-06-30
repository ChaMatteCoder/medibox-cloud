# MediBox Cloud

MediBox Cloud é uma base backend acadêmica para controle inteligente de medicamentos. O projeto simula uma caixa inteligente capaz de enviar eventos para a nuvem, enquanto cuidadores cadastram pacientes, medicamentos e horários de uso.

O foco é demonstrar uma arquitetura backend simples, modular e explicável usando Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT, RabbitMQ, Docker Compose, NGINX e uma base inicial para Kubernetes.

Esta base evita funcionalidades fora do escopo para manter o projeto legível em uma apresentação de Arquitetura de Software Aplicada.

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

## Serviços

`auth-service`

- Cadastro de usuário.
- Login com JWT.
- Endpoint `/auth/me`.
- Papéis: `ADMIN`, `CAREGIVER`, `PATIENT`.
- Camadas internas: routes, schemas, models, repositories e services.

`medication-service`

- Cadastro e consulta de pacientes.
- Cadastro e consulta de medicamentos.
- Cadastro e consulta de horários por paciente.
- Regras de aplicação concentradas em services, não nas rotas.

`event-service`

- Registro de eventos da caixa inteligente.
- Publicação de mensagens na fila `medibox.notifications`.
- Publicação em RabbitMQ após persistir o evento no banco.
- Resumo simples de adesão por paciente com base nos eventos de dose.

`notification-worker`

- Consome mensagens do RabbitMQ.
- Simula notificações por logs no terminal.
- Não expõe API HTTP nesta versão.
- Diferencia notificações comuns de eventos críticos.

## Como Rodar com Docker Compose

Na raiz do projeto:

```bash
docker compose up --build
```

O Compose lê variáveis de ambiente a partir de `.env.example`. Os valores desse arquivo são exemplos para desenvolvimento local e apresentação acadêmica, não segredos de produção.

Se quiser trocar credenciais ou URLs localmente, edite uma cópia do arquivo e ajuste o `env_file` no `docker-compose.yml`:

```bash
cp .env.example .env
```

Para a validação padrão do projeto, basta manter `.env.example` como está.

Depois acesse:

- Gateway: http://localhost
- RabbitMQ Management: http://localhost:15672
- Usuário RabbitMQ: `medibox`
- Senha RabbitMQ: `medibox`

Se o comando falhar com erro de conexão no `dockerDesktopLinuxEngine`, abra o Docker Desktop e aguarde a engine Linux iniciar antes de rodar o Compose novamente.

## Documentação Swagger

Pelo gateway:

- Auth: http://localhost/auth/docs
- Medications: http://localhost/medications/docs
- Events: http://localhost/events/docs

Portas diretas dos serviços:

- Auth service: http://localhost:8001/auth/docs
- Medication service: http://localhost:8002/medications/docs
- Event service: http://localhost:8003/events/docs

## Endpoints Principais

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
GET  /patients/{patient_id}/adherence-summary
GET  /health
```

As rotas de pacientes, medicamentos, horários e eventos exigem Bearer Token gerado pelo `auth-service`.

As rotas `/health` dos serviços existem nas portas diretas. Pelo gateway, `http://localhost/health` valida o NGINX.

## Regras de Negócio Atuais

Resumo de adesão:

- Endpoint: `GET /patients/{patient_id}/adherence-summary`.
- Implementado no `event-service`, pois o cálculo depende dos eventos registrados pela caixa.
- Retorna `total_events`, `doses_taken`, `doses_missed`, `doses_delayed` e `adherence_rate`.
- A taxa de adesão usa a fórmula: `doses_taken / (doses_taken + doses_missed + doses_delayed) * 100`.
- Eventos como `BOX_OPENED` e `ALERT_TRIGGERED` entram em `total_events`, mas não entram no denominador da taxa.

Notificações críticas:

- Eventos críticos: `DOSE_MISSED`, `DOSE_DELAYED`, `ALERT_TRIGGERED`.
- O `notification-worker` registra logs prioritários para eventos críticos.
- Os demais eventos geram notificações comuns simuladas.

## Fluxo Rápido de Teste

1. Cadastre um usuário:

```bash
curl -X POST http://localhost/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Ana Cuidadora\",\"email\":\"ana@example.com\",\"password\":\"123456\",\"role\":\"CAREGIVER\"}"
```

2. Faça login e copie o `access_token`:

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

## Testes Automatizados

Os testes usam `pytest` e `httpx` por meio do cliente de teste do FastAPI. Eles são simples e validam os endpoints principais sem exigir PostgreSQL ou RabbitMQ reais: cada serviço usa SQLite em memória durante o teste, e o envio ao RabbitMQ é simulado no `event-service`.

Como os serviços usam o mesmo nome de pacote Python (`app`), execute os testes por serviço.

Com Python local:

```bash
cd services/auth-service
python -m pip install -r requirements.txt
python -m pytest

cd ../medication-service
python -m pip install -r requirements.txt
python -m pytest

cd ../event-service
python -m pip install -r requirements.txt
python -m pytest
```

Com PowerShell, a partir da raiz:

```powershell
Push-Location services/auth-service
python -m pip install -r requirements.txt
python -m pytest
Pop-Location

Push-Location services/medication-service
python -m pip install -r requirements.txt
python -m pytest
Pop-Location

Push-Location services/event-service
python -m pip install -r requirements.txt
python -m pytest
Pop-Location
```

Também é possível rodar pelos containers, depois de construir as imagens:

```bash
docker compose build auth-service medication-service event-service
docker compose run --rm --no-deps auth-service pytest
docker compose run --rm --no-deps medication-service pytest
docker compose run --rm --no-deps event-service pytest
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
[NOTIFICATION] Paciente X gerou evento DOSE_TAKEN. Notificação comum simulada registrada.
```

Para eventos críticos, o log esperado segue o formato:

```txt
[CRITICAL NOTIFICATION] Paciente X gerou evento crítico DOSE_MISSED. Alerta prioritário simulado enviado ao cuidador.
```

## Banco e Migrations

O projeto usa PostgreSQL com um banco compartilhado para simplificar a apresentação acadêmica.

Cada serviço com banco possui seu próprio Alembic:

- `services/auth-service/alembic`
- `services/medication-service/alembic`
- `services/event-service/alembic`

Cada um usa uma tabela de versão própria, evitando conflito no banco compartilhado.

Essa escolha reduz a complexidade operacional inicial. Em uma evolução mais próxima de produção, cada serviço poderia ter seu próprio banco.

## Kubernetes

Os manifests básicos ficam em:

```txt
infra/k8s/
```

Arquivos incluídos:

- namespace;
- ConfigMap;
- Secret de exemplo;
- PostgreSQL;
- RabbitMQ;
- deployments dos serviços;
- services internos;
- NGINX gateway;
- ingress.

Para validação local com Kind, consulte [docs/kind-validation.md](docs/kind-validation.md).

Antes de aplicar em um cluster real, copie `secret.example.yaml`, ajuste os segredos e publique as imagens Docker com nomes acessíveis ao cluster.

Exemplo de aplicação:

```bash
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/configmap.yaml
kubectl apply -f infra/k8s/secret.example.yaml
kubectl apply -f infra/k8s/
```

## Próximos Passos Possíveis

- Criar endpoints para solicitação de mudança de horário pelo paciente.
- Adicionar autorização por papel em rotas sensíveis.
- Melhorar observabilidade com logs estruturados.
- Separar bancos por serviço em uma evolução da arquitetura.
- Criar pipeline CI/CD.
- Evoluir os manifests Kubernetes para Helm quando fizer sentido.
