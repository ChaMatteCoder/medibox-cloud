# Arquitetura da MediBox Cloud

A MediBox Cloud foi organizada como um monorepo com servicos pequenos e responsabilidades claras.

## Visao geral

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

## Servicos

- `auth-service`: cadastro, login, JWT e usuario autenticado.
- `medication-service`: pacientes, medicamentos e horarios.
- `event-service`: eventos enviados pela caixa inteligente.
- `notification-worker`: consumidor assincrono da fila de notificacoes.

## Decisoes de simplicidade

- Um unico banco PostgreSQL e usado para a primeira versao academica.
- Cada servico mantem seus modelos e migrations separados.
- O `event-service` publica uma mensagem simples no RabbitMQ apos registrar um evento.
- O worker simula o envio de notificacao apenas por logs.
- O Kubernetes usa manifests puros, sem Helm.
