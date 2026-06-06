# Lab 7 – Observability (Prometheus, Grafana, Tempo)

## Описание

В данной лабораторной работе реализована система наблюдаемости (observability) для backend-приложения на Flask.

Реализованы:
- метрики (Prometheus)
- логирование (Loki)
- распределённый трейсинг (Tempo)
- визуализация (Grafana)

---

## 1. Метрики

В приложении реализован endpoint:

```
/metrics
```

Добавлены метрики:

- HTTP counter:
```
flask_http_requests_total
```

- Histogram (время ответа):
```
flask_http_request_duration_seconds
```

- Бизнес-метрика:
```
flask_business_requests_total
```

- Gauge:
```
flask_in_progress_requests
```

Метрики используют labels с умеренной кардинальностью:
- method
- endpoint
- status

---

## 2. Скрейпинг (Prometheus)

Для сбора метрик в Kubernetes создан объект:

```
ServiceMonitor
```

Prometheus автоматически собирает метрики с Flask:

```
/metrics
```

Проверка:
- Prometheus → Status → Targets
- target Flask в статусе:

```
UP
```

---

## 3. Трейсинг (Tempo)

Tempo развёрнут в Kubernetes:

```bash
helm install tempo grafana/tempo
```

В приложении добавлен OpenTelemetry:

- автоматическая инструментализация Flask
- экспорт trace через OTLP

Endpoint для отправки trace:

```
http://tempo:4318/v1/traces
```

Проверка:
- Grafana → Explore → Tempo
- найден trace по HTTP-запросу к API

---

## 4. Grafana

Подключены datasources:

- Prometheus
- Tempo

Создан dashboard с метриками:

- Requests per second:

```promql
sum(rate(flask_http_requests_total[1m]))
```

- Business metric:

```promql
flask_business_requests_total
```

- Latency (P95):

```promql
histogram_quantile(0.95, sum(rate(flask_http_request_duration_seconds_bucket[1m])) by (le))
```

---

## 5. Скриншоты

В отчёте представлены:

- Prometheus → Targets (Flask target = UP)
- Grafana → Dashboard с метриками backend
- Grafana → Explore → Tempo (trace с HTTP-запросом)

Рекомендуемая структура:

```
docs/screenshots/lab7/
```

---

## Конфигурации observability

В репозитории добавлены конфигурации платформенного стека:

- `observability/prometheus/prometheus.yaml` — scrape config для Flask-приложения
- `observability/tempo/tempo.yaml` — конфигурация Tempo и OTLP receivers
- `observability/grafana/provisioning/datasources/datasources.yaml` — datasources Prometheus и Tempo
- `observability/grafana/provisioning/dashboards/dashboard-provider.yaml` — provider для dashboard
- `observability/grafana/dashboards/flask-dashboard.json` — dashboard с PromQL-панелями
- `k8s/servicemonitor.yaml` — ServiceMonitor для Kubernetes scraping

---

## Итог

В лабораторной реализована полноценная система наблюдаемости:

- сбор метрик через Prometheus
- визуализация в Grafana
- логирование через Loki
- распределённый трейсинг через Tempo

Приложение полностью интегрировано в observability стек.
