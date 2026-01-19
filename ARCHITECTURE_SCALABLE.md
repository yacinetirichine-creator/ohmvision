# OhmVision - Architecture Scalable & Haute Disponibilité

## 🎯 Objectif

Transformer l'architecture actuelle **monolithe** en une architecture **scalable** supportant:
- **1 000+ caméras** par instance
- **Haute disponibilité** (99.9% uptime)
- **Multi-région** (edge + cloud)
- **Load balancing** automatique

---

## 🏗️ Architecture Actuelle vs Cible

### ❌ ACTUEL (Monolithe)

```
┌─────────────────────────────────────┐
│     Single Docker Container         │
│                                     │
│  FastAPI + IA + PostgreSQL + Redis │
│                                     │
│  Limites:                          │
│  - 1 serveur = SPOF                │
│  - Pas de scaling horizontal       │
│  - Performance limitée             │
└─────────────────────────────────────┘
```

### ✅ CIBLE (Microservices + Edge)

```
┌────────────────────────── CLOUD ─────────────────────────────┐
│                                                               │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │ Load Balancer│─────▶│   API        │ (3+ instances)      │
│  │  (HAProxy)   │      │  Gateway     │                     │
│  └──────────────┘      └──────────────┘                     │
│         │                      │                             │
│         │              ┌───────┴────────┐                   │
│         │              ▼                ▼                    │
│         │      ┌──────────────┐  ┌──────────────┐          │
│         │      │  Auth        │  │  Analytics   │          │
│         │      │  Service     │  │  Service     │          │
│         │      └──────────────┘  └──────────────┘          │
│         │                                                    │
│         ├─────────────────┐                                 │
│         ▼                 ▼                                 │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │ PostgreSQL   │  │    Redis     │                       │
│  │  (Primary +  │  │  (Sentinel)  │                       │
│  │   Replicas)  │  │              │                       │
│  └──────────────┘  └──────────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                         ▲
                         │ Métadonnées + Alertes
                         │
┌────────────────────── EDGE ──────────────────────────────────┐
│                                                               │
│  Site Client 1              Site Client 2                    │
│  ┌──────────────────┐       ┌──────────────────┐           │
│  │  Edge Processor  │       │  Edge Processor  │           │
│  │                  │       │                  │           │
│  │  • IA locale     │       │  • IA locale     │           │
│  │  • Enregistrement│       │  • Enregistrement│           │
│  │  • 10-50 caméras │       │  • 10-50 caméras │           │
│  │                  │       │                  │           │
│  └──────────────────┘       └──────────────────┘           │
│         ▲                            ▲                       │
│         │                            │                       │
│    [Caméras 1-50]              [Caméras 51-100]            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Services Décomposés

### 1. **API Gateway** (Kong / Traefik)
- Point d'entrée unique
- Rate limiting
- Authentication
- Routing vers services

### 2. **Auth Service**
- JWT tokens
- User management
- OAuth2/OIDC
- MFA

### 3. **Camera Management Service**
- CRUD caméras
- Discovery ONVIF
- Health checks

### 4. **AI Processing Service** (Scalable horizontalement)
- Queue de traitement (RabbitMQ/Kafka)
- Workers IA (auto-scaling)
- GPU pool management

### 5. **Analytics Service**
- Agrégation données
- Rapports
- Dashboards temps réel

### 6. **Storage Service**
- Gestion vidéos
- Tiering automatique
- S3/MinIO

### 7. **Alert Service**
- Notifications temps réel
- WebSocket server
- Email/SMS/Push

---

## 🚀 Technologies de Scaling

### **Load Balancing**

**HAProxy Configuration:**

```haproxy
# /etc/haproxy/haproxy.cfg

frontend ohmvision_api
    bind *:80
    bind *:443 ssl crt /etc/ssl/certs/ohmvision.pem
    
    # Rate limiting
    stick-table type ip size 100k expire 30s store http_req_rate(10s)
    http-request track-sc0 src
    http-request deny if { sc_http_req_rate(0) gt 100 }
    
    # Routing
    acl is_api path_beg /api
    acl is_ws path_beg /ws
    
    use_backend api_servers if is_api
    use_backend websocket_servers if is_ws

backend api_servers
    balance roundrobin
    option httpchk GET /health
    
    server api1 10.0.1.10:8000 check
    server api2 10.0.1.11:8000 check
    server api3 10.0.1.12:8000 check

backend websocket_servers
    balance leastconn
    option httpchk GET /health
    
    server ws1 10.0.1.20:8000 check
    server ws2 10.0.1.21:8000 check
```

### **PostgreSQL High Availability (Patroni + etcd)**

```yaml
# patroni.yml
scope: ohmvision-cluster
namespace: /ohmvision/
name: postgresql1

restapi:
  listen: 0.0.0.0:8008
  connect_address: 10.0.1.30:8008

etcd:
  hosts: 
    - 10.0.1.40:2379
    - 10.0.1.41:2379
    - 10.0.1.42:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576
    
  postgresql:
    use_pg_rewind: true
    parameters:
      max_connections: 500
      shared_buffers: 4GB
      effective_cache_size: 12GB
      wal_level: replica
      max_wal_senders: 10

postgresql:
  listen: 0.0.0.0:5432
  connect_address: 10.0.1.30:5432
  data_dir: /var/lib/postgresql/14/main
  
  authentication:
    replication:
      username: replicator
      password: changeme
    superuser:
      username: postgres
      password: changeme

  parameters:
    max_connections: 500
```

**Résultat:**
- Primary + 2 Replicas (read-only)
- Failover automatique < 30s
- Read queries distribuées

### **Redis Sentinel (High Availability)**

```yaml
# docker-compose.redis-sentinel.yml
version: '3.8'

services:
  redis-master:
    image: redis:7-alpine
    command: redis-server --requirepass ohmvision_redis
    ports:
      - "6379:6379"
  
  redis-replica-1:
    image: redis:7-alpine
    command: redis-server --slaveof redis-master 6379 --masterauth ohmvision_redis
    depends_on:
      - redis-master
  
  redis-replica-2:
    image: redis:7-alpine
    command: redis-server --slaveof redis-master 6379 --masterauth ohmvision_redis
    depends_on:
      - redis-master
  
  sentinel-1:
    image: redis:7-alpine
    command: redis-sentinel /etc/redis/sentinel.conf
    volumes:
      - ./sentinel.conf:/etc/redis/sentinel.conf
    depends_on:
      - redis-master
  
  sentinel-2:
    image: redis:7-alpine
    command: redis-sentinel /etc/redis/sentinel.conf
    volumes:
      - ./sentinel.conf:/etc/redis/sentinel.conf
    depends_on:
      - redis-master
  
  sentinel-3:
    image: redis:7-alpine
    command: redis-sentinel /etc/redis/sentinel.conf
    volumes:
      - ./sentinel.conf:/etc/redis/sentinel.conf
    depends_on:
      - redis-master
```

**sentinel.conf:**
```
sentinel monitor mymaster redis-master 6379 2
sentinel auth-pass mymaster ohmvision_redis
sentinel down-after-milliseconds mymaster 5000
sentinel parallel-syncs mymaster 1
sentinel failover-timeout mymaster 10000
```

### **Message Queue (RabbitMQ pour AI Tasks)**

```yaml
# docker-compose.rabbitmq.yml
version: '3.8'

services:
  rabbitmq:
    image: rabbitmq:3-management-alpine
    environment:
      RABBITMQ_DEFAULT_USER: ohmvision
      RABBITMQ_DEFAULT_PASS: changeme
    ports:
      - "5672:5672"   # AMQP
      - "15672:15672" # Management UI
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq

volumes:
  rabbitmq_data:
```

**Usage Python (Producer):**
```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('rabbitmq')
)
channel = connection.channel()

channel.queue_declare(queue='ai_processing', durable=True)

# Envoyer frame pour traitement IA
message = {
    "camera_id": 1,
    "frame_data": "base64...",
    "timestamp": "2026-01-19T12:00:00"
}

channel.basic_publish(
    exchange='',
    routing_key='ai_processing',
    body=json.dumps(message),
    properties=pika.BasicProperties(
        delivery_mode=2,  # Persistent
    )
)
```

**Worker (Consumer):**
```python
def process_frame(ch, method, properties, body):
    data = json.loads(body)
    
    # Traiter avec IA
    detections = ai_engine.process(data["frame_data"])
    
    # ACK
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='ai_processing', on_message_callback=process_frame)

channel.start_consuming()
```

---

## 📊 Auto-Scaling (Kubernetes)

### **Deployment avec HPA (Horizontal Pod Autoscaler)**

```yaml
# k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ohmvision-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ohmvision-api
  template:
    metadata:
      labels:
        app: ohmvision-api
    spec:
      containers:
      - name: api
        image: ohmvision/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: ohmvision-api-service
spec:
  selector:
    app: ohmvision-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ohmvision-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ohmvision-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Résultat:**
- 3-10 instances selon charge
- Scale up si CPU > 70% ou RAM > 80%
- Scale down automatique

---

## 🌍 Multi-Région (Edge + Cloud)

### **Architecture Hybrid**

```python
# backend/core/edge_coordinator.py

class EdgeCoordinator:
    """
    Coordonnateur Edge-Cloud
    
    - IA locale sur Edge (faible latence)
    - Métadonnées sync vers Cloud
    - Failover automatique
    """
    
    def __init__(self, cloud_endpoint: str, edge_mode: bool = False):
        self.cloud_endpoint = cloud_endpoint
        self.edge_mode = edge_mode
        self.local_queue = deque(maxlen=10000)
        
    async def process_frame(self, camera_id: int, frame: np.ndarray):
        """Traiter frame (edge ou cloud)"""
        
        if self.edge_mode:
            # Traitement local
            detections = await self.local_ai.process(frame)
            
            # Sync métadonnées vers cloud (async)
            asyncio.create_task(
                self.sync_to_cloud(camera_id, detections)
            )
        else:
            # Envoi vers cloud
            detections = await self.send_to_cloud(camera_id, frame)
        
        return detections
    
    async def sync_to_cloud(self, camera_id: int, detections: List):
        """Synchroniser métadonnées vers cloud"""
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.cloud_endpoint}/api/detections",
                    json={
                        "camera_id": camera_id,
                        "detections": [d.to_dict() for d in detections],
                        "timestamp": datetime.now().isoformat()
                    },
                    timeout=5.0
                )
        except Exception as e:
            # Ajouter à la queue locale pour retry
            self.local_queue.append({
                "camera_id": camera_id,
                "detections": detections
            })
            logger.warning(f"Cloud sync failed, queued: {e}")
```

---

## 📈 Capacité Cible

| Métrique | Actuel | Cible |
|----------|--------|-------|
| **Caméras / instance** | 10-20 | 1000+ |
| **Requêtes / sec** | 100 | 10,000+ |
| **Uptime** | 95% | 99.9% |
| **Latence API** | 200ms | <50ms |
| **Failover time** | Manuel | <30s auto |
| **Scaling** | Manuel | Auto (HPA) |

---

## ✅ Implémentation Progressive

### Phase 1 (1 mois)
- [ ] Séparer services (Auth, Camera, AI)
- [ ] Setup RabbitMQ pour AI queue
- [ ] PostgreSQL réplication (1 replica)

### Phase 2 (2 mois)
- [ ] Load balancer HAProxy
- [ ] Redis Sentinel
- [ ] Monitoring (Prometheus + Grafana)

### Phase 3 (3 mois)
- [ ] Kubernetes deployment
- [ ] Auto-scaling HPA
- [ ] Multi-région edge

---

## 🔧 Outils de Monitoring

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  grafana_data:
```

Dashboards:
- CPU/RAM par service
- Requêtes/sec
- Latence P50/P95/P99
- Taux d'erreur
- Queue depth (RabbitMQ)
