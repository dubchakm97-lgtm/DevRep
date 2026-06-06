# Lab 6 – Infrastructure (PostgreSQL)

## Описание

В данной лабораторной работе реализована инфраструктура для приложения с использованием Kubernetes.

Решение разделено на два подхода управления инфраструктурой:

- **Kustomize** — для инфраструктуры PostgreSQL
- **Helm** — для приложения Flask

Инфраструктура включает:

- PostgreSQL (StatefulSet)
- Service для доступа к БД
- ConfigMap для конфигурации
- Secret для хранения пароля
- PersistentVolumeClaim для хранения данных
- Helm chart для приложения

Подготовлены два окружения:

- dev (для разработки)
- prod (для продакшена)

---

## Структура проекта

```text
Lab6/
  k8s/
    kustomization/
      base/
      overlays/
        dev/
        prod/

    helm/
      flask-app/
        Chart.yaml
        values.yaml
        values-dev.yaml
        values-prod.yaml

        templates/
          deployment.yaml
          service.yaml
          ingress.yaml
          configmap.yaml
          secret.yaml
```

### Назначение каталогов

#### Kustomize

- `base` — базовые манифесты PostgreSQL
- `overlays/dev` — конфигурация окружения разработки
- `overlays/prod` — конфигурация продакшен окружения

#### Helm

- `Chart.yaml` — описание Helm chart
- `values.yaml` — общие параметры
- `values-dev.yaml` — настройки dev
- `values-prod.yaml` — настройки prod
- `templates/` — шаблоны Kubernetes ресурсов

---

## Контракт для приложения

Приложение использует следующие переменные окружения:

```text
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

Подключение выполняется по адресу:

```text
postgres.<namespace>.svc.cluster.local:5432
```

Примеры:

dev:

```text
postgres.flask-dev.svc.cluster.local:5432
```

prod:

```text
postgres.flask-prod.svc.cluster.local:5432
```

---

## Деплой инфраструктуры (Kustomize)

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

## Деплой приложения (Helm)

Проверка шаблонов:

```bash
helm template flask-app ./k8s/helm/flask-app \
-f ./k8s/helm/flask-app/values-dev.yaml
```

Установка dev:

```bash
helm upgrade --install flask-app \
./k8s/helm/flask-app \
--namespace flask-dev \
--create-namespace \
-f ./k8s/helm/flask-app/values-dev.yaml
```

Установка prod:

```bash
helm upgrade --install flask-app \
./k8s/helm/flask-app \
--namespace flask-prod \
--create-namespace \
-f ./k8s/helm/flask-app/values-prod.yaml
```

---

## Проверка инфраструктуры

```bash
kubectl get pods,svc,pvc -n flask-dev
kubectl get pods,svc,pvc -n flask-prod
```

Проверка логов PostgreSQL:

```bash
kubectl logs -n flask-dev postgres-0
kubectl logs -n flask-prod postgres-0
```

Ожидаемый результат:

```text
database system is ready to accept connections
```

---

## Порядок запуска

### 1. Развернуть инфраструктуру PostgreSQL

```bash
kubectl apply -k k8s/kustomization/overlays/dev
```

Проверка:

```bash
kubectl get pods -n flask-dev
```

---

### 2. Развернуть приложение через Helm

```bash
helm upgrade --install flask-app \
./k8s/helm/flask-app \
-f ./k8s/helm/flask-app/values-dev.yaml
```

---

### 3. Проверить приложение

Приложение доступно:

```text
http://flask.local/
```

Проверка:

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

Удаление инфраструктуры:

```bash
kubectl delete -k k8s/kustomization/overlays/dev
kubectl delete -k k8s/kustomization/overlays/prod
```

Удаление приложения:

```bash
helm uninstall flask-app -n flask-dev
helm uninstall flask-app -n flask-prod
```

---

## Итог

В лабораторной реализованы:

- инфраструктура PostgreSQL через Kustomize
- разделение на dev и prod окружения
- контракт подключения приложения
- Helm chart для приложения
- параметризация через values-файлы
- развёртывание и управление Kubernetes ресурсами