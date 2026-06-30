# Arquitetura da MediBox Cloud

A MediBox Cloud foi organizada como um monorepo com servicos pequenos e responsabilidades claras. A proposta e didatica: mostrar separacao de responsabilidades, persistencia, autenticacao, mensageria e gateway sem transformar o projeto em uma plataforma grande demais para apresentar.

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

## Organizacao interna

Os servicos FastAPI seguem a mesma divisao basica:

- `api/routes`: entrada HTTP, validacao de dependencias e chamada da camada de servico.
- `schemas`: modelos Pydantic de entrada e saida.
- `db/models`: entidades SQLAlchemy.
- `repositories`: acesso ao banco de dados.
- `services`: regras de aplicacao e orquestracao.
- `core/config.py`: leitura de variaveis de ambiente.

Essa separacao evita colocar regra de negocio diretamente nos controllers.

## Configuracao

As configuracoes de banco, JWT e RabbitMQ sao lidas por variaveis de ambiente. O arquivo `.env.example` traz valores de desenvolvimento local para facilitar a validacao academica.

Em producao, esses valores devem ser substituidos por secrets reais, fora do repositorio.

## Decisoes de simplicidade

- Um unico banco PostgreSQL e usado para a primeira versao academica.
- Cada servico mantem seus modelos e migrations separados.
- O `event-service` publica uma mensagem simples no RabbitMQ apos registrar um evento.
- O worker simula o envio de notificacao apenas por logs.
- O Kubernetes usa manifests puros, sem Helm.

## Fluxo principal

1. O cuidador se cadastra e faz login no `auth-service`.
2. O token JWT e usado nas rotas protegidas.
3. O `medication-service` registra pacientes, medicamentos e agendas.
4. A caixa inteligente envia eventos para o `event-service`.
5. O `event-service` salva o evento e publica uma mensagem no RabbitMQ.
6. O `notification-worker` consome a mensagem e simula o alerta ao cuidador.
