# Arquitetura da MediBox Cloud

A MediBox Cloud foi organizada como um monorepo com serviços pequenos e responsabilidades claras. A proposta é didática: mostrar separação de responsabilidades, persistência, autenticação, mensageria e gateway sem transformar o projeto em uma plataforma grande demais para apresentar.

## Visão Geral

```txt
Cliente / Caixa Inteligente
        |
        v
  NGINX API Gateway
        |
        +--> auth-service
        +--> medication-service
        +--> event-service ----> RabbitMQ ----> notification-worker
                         |
                         v
                    PostgreSQL
```

## Serviços

- `auth-service`: cadastro, login, JWT e usuário autenticado.
- `medication-service`: pacientes, medicamentos e horários.
- `event-service`: eventos enviados pela caixa inteligente e resumo de adesão.
- `notification-worker`: consumidor assíncrono da fila de notificações.

## Organização Interna

Os serviços FastAPI seguem a mesma divisão básica:

- `api/routes`: entrada HTTP, validação de dependências e chamada da camada de serviço.
- `schemas`: modelos Pydantic de entrada e saída.
- `db/models`: entidades SQLAlchemy.
- `repositories`: acesso ao banco de dados.
- `services`: regras de aplicação e orquestração.
- `core/config.py`: leitura de variáveis de ambiente.

Essa separação evita colocar regra de negócio diretamente nos controllers.

## Configuração

As configurações de banco, JWT e RabbitMQ são lidas por variáveis de ambiente. O arquivo `.env.example` traz valores de desenvolvimento local para facilitar a validação acadêmica.

Em produção, esses valores devem ser substituídos por secrets reais, fora do repositório.

## Kubernetes

Os manifests ficam em `infra/k8s/` e foram organizados para demonstrar uma implantação simples, sem Helm:

- `namespace.yaml`: cria o namespace `medibox`.
- `configmap.yaml`: concentra configurações não sensíveis e a configuração do NGINX Gateway.
- `secret.example.yaml`: exemplo didático dos segredos necessários.
- `*-deployment.yaml`: define os pods de PostgreSQL, RabbitMQ, serviços FastAPI, worker e gateway.
- `*-service.yaml`: expõe os serviços internamente no cluster.
- `ingress.yaml`: encaminha tráfego externo para o `gateway-service`.

Fluxo esperado no cluster:

```txt
Ingress
  |
  v
gateway-service -> nginx-gateway
  |
  +--> auth-service
  +--> medication-service
  +--> event-service
```

O PostgreSQL e o RabbitMQ ficam acessíveis apenas por Services internos. O `notification-worker` não possui Service porque não recebe tráfego HTTP; ele apenas consome mensagens do RabbitMQ.

Os serviços FastAPI possuem `readinessProbe` e `livenessProbe` em `/health`. O gateway também possui probes em `/health`. Esses probes ajudam o Kubernetes a saber quando o container está pronto para receber tráfego e quando precisa ser reiniciado.

Para validação local com Kind, use o guia completo em [kind-validation.md](kind-validation.md).

A ideia geral é:

```bash
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/configmap.yaml
kubectl apply -f infra/k8s/secret.example.yaml
kubectl apply -f infra/k8s/
```

Antes de rodar em Kind, as imagens locais precisam ser construídas e carregadas no cluster:

```txt
medibox-auth-service:local
medibox-medication-service:local
medibox-event-service:local
medibox-notification-worker:local
```

Em um cluster remoto, essas imagens deveriam ser publicadas em um registry acessível ao cluster.

## Decisões de Simplicidade

- Um único banco PostgreSQL é usado para a primeira versão acadêmica.
- Cada serviço mantém seus modelos e migrations separados.
- O `event-service` publica uma mensagem simples no RabbitMQ após registrar um evento.
- O `event-service` calcula um resumo simples de adesão por paciente a partir dos eventos de dose.
- O worker simula o envio de notificação por logs e destaca eventos críticos.
- O Kubernetes usa manifests puros, sem Helm.

## Regras de Negócio

### Resumo de Adesão

O endpoint `GET /patients/{patient_id}/adherence-summary` é atendido pelo `event-service`, mesmo usando o caminho `/patients`, porque o dado calculado vem dos eventos da caixa inteligente.

O gateway encaminha apenas esse caminho específico para o `event-service`. As demais rotas `/patients` continuam no `medication-service`.

Campos retornados:

- `total_events`: quantidade total de eventos do paciente.
- `doses_taken`: quantidade de eventos `DOSE_TAKEN`.
- `doses_missed`: quantidade de eventos `DOSE_MISSED`.
- `doses_delayed`: quantidade de eventos `DOSE_DELAYED`.
- `adherence_rate`: percentual de doses tomadas sobre eventos de dose.

Fórmula:

```txt
doses_taken / (doses_taken + doses_missed + doses_delayed) * 100
```

### Notificações Críticas

O `notification-worker` classifica como críticos:

- `DOSE_MISSED`
- `DOSE_DELAYED`
- `ALERT_TRIGGERED`

Esses eventos geram logs prioritários. Os outros eventos geram logs comuns.

## Fluxo Principal

1. O cuidador se cadastra e faz login no `auth-service`.
2. O token JWT é usado nas rotas protegidas.
3. O `medication-service` registra pacientes, medicamentos e agendas.
4. A caixa inteligente envia eventos para o `event-service`.
5. O `event-service` salva o evento e publica uma mensagem no RabbitMQ.
6. O `notification-worker` consome a mensagem e simula o alerta ao cuidador.
7. O cuidador pode consultar o resumo de adesão calculado a partir dos eventos do paciente.
