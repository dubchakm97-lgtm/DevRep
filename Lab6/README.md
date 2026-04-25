# Lab 6 – Infrastructure (PostgreSQL)

## Описание

В данной лабораторной работе реализована инфраструктура для приложения с использованием Kubernetes.

Инфраструктура включает:
- PostgreSQL (StatefulSet)
- Service для доступа к БД
- ConfigMap для конфигурации
- Secret для хранения пароля
- PersistentVolumeClaim для хранения данных

Разделены два окружения:
- dev (для разработки)
- prod (для продакшена)

---

## Структура проекта

```
Lab6/
  k8s/
    kustomization/
      base/
      overlays/
        dev/
        prod/
```

- base – общие манифесты PostgreSQL  
- overlays/dev – конфигурация для dev  
- overlays/prod – конфигурация для prod  

---

## Контракт для приложения

Приложение должно использовать следующие переменные окружения:

```
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

Подключение к базе осуществляется по адресу:

```
postgres.<namespace>.svc.cluster.local:5432
```

Примеры:

dev:
```
postgres.flask-dev.svc.cluster.local:5432
```

prod:
```
postgres.flask-prod.svc.cluster.local:5432
```

---

## Деплой

### Dev

```bash
kubectl create namespace flask-dev
kubectl apply -k k8s/kustomization/overlays/dev
```

### Prod

```bash
kubectl create namespace flask-prod
kubectl apply -k k8s/kustomization/overlays/prod
```

---

## Проверка

```bash
kubectl get pods,svc,pvc -n flask-dev
kubectl get pods,svc,pvc -n flask-prod
```

Проверка логов:

```bash
kubectl logs -n flask-dev postgres-0
kubectl logs -n flask-prod postgres-0
```

Ожидаемый результат:

```
database system is ready to accept connections
```

---

## Порядок запуска инфраструктуры и приложения

Сначала разворачивается инфраструктура PostgreSQL:

```bash
kubectl apply -k k8s/kustomization/overlays/dev
```

Проверка инфраструктуры:

```bash
kubectl get pods,svc,pvc -n flask-dev
kubectl logs -n flask-dev postgres-0
```

Ожидаемый результат:

```
database system is ready to accept connections
```

После этого разворачивается приложение из лабораторной №5.

Приложение доступно через Ingress:

```
http://flask.local/
```

Проверка backend-приложения:

```bash
curl http://flask.local/
```

Пример ответа:

```json
{
  "api_key_loaded": true,
  "app_env": "production",
  "log_level": "info",
  "message": "Hello from Flask with Prometheus metrics!",
  "status": "running"
}
```

---

## Удаление

```bash
kubectl delete -k k8s/kustomization/overlays/dev
kubectl delete -k k8s/kustomization/overlays/prod
```

---

## Итог

Инфраструктура разделена на base и overlays, что позволяет:
- переиспользовать конфигурацию
- управлять dev/prod окружениями
- избегать дублирования YAML