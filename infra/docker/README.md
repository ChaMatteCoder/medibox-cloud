# Docker

Os Dockerfiles ficam dentro de cada servico para manter o monorepo simples.

O arquivo `docker-compose.yml` da raiz sobe:

- PostgreSQL;
- RabbitMQ com painel de gerenciamento;
- auth-service;
- medication-service;
- event-service;
- notification-worker;
- NGINX como API Gateway.
