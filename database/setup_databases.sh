#!/bin/bash
# Database Setup Script für KI Agent Orchestrator System
# Erstellt alle benötigten Datenbanken mit verschiedenen Ports

set -e

echo "🔧 Setting up KI Agent Database Infrastructure..."

# Ports Definition
POSTGRES_PORT=5433
REDIS_PORT=6380
QDRANT_PORT=6334
MONGO_PORT=27018
ELASTICSEARCH_PORT=9201

# Verzeichnisse erstellen
sudo mkdir -p /opt/ki-agent/data/{postgres,redis,qdrant,mongo,elasticsearch}
sudo mkdir -p /opt/ki-agent/logs
sudo mkdir -p /opt/ki-agent/configs

# PostgreSQL Setup (für Audit & Metadaten)
echo "📊 Setting up PostgreSQL on port $POSTGRES_PORT..."
sudo docker run -d \
  --name ki-agent-postgres \
  --restart unless-stopped \
  -e POSTGRES_USER=ki_agent \
  -e POSTGRES_PASSWORD=SecureKIAgent2025! \
  -e POSTGRES_DB=ki_agent_db \
  -p $POSTGRES_PORT:5432 \
  -v /opt/ki-agent/data/postgres:/var/lib/postgresql/data \
  -v /opt/ki-agent/configs/postgres.conf:/etc/postgresql/postgresql.conf \
  postgres:15-alpine

# Redis Setup (für Caching & Session Management)
echo "🚀 Setting up Redis on port $REDIS_PORT..."
sudo docker run -d \
  --name ki-agent-redis \
  --restart unless-stopped \
  -p $REDIS_PORT:6379 \
  -v /opt/ki-agent/data/redis:/data \
  -v /opt/ki-agent/configs/redis.conf:/usr/local/etc/redis/redis.conf \
  redis:7-alpine redis-server /usr/local/etc/redis/redis.conf

# Qdrant Setup (für Vector Embeddings)
echo "🧠 Setting up Qdrant Vector DB on port $QDRANT_PORT..."
sudo docker run -d \
  --name ki-agent-qdrant \
  --restart unless-stopped \
  -p $QDRANT_PORT:6333 \
  -p 6334:6334 \
  -v /opt/ki-agent/data/qdrant:/qdrant/storage \
  qdrant/qdrant:v1.10.0

# MongoDB Setup (für Document Storage & Logs)
echo "📄 Setting up MongoDB on port $MONGO_PORT..."
sudo docker run -d \
  --name ki-agent-mongo \
  --restart unless-stopped \
  -e MONGO_INITDB_ROOT_USERNAME=ki_agent \
  -e MONGO_INITDB_ROOT_PASSWORD=SecureKIAgent2025! \
  -p $MONGO_PORT:27017 \
  -v /opt/ki-agent/data/mongo:/data/db \
  mongo:7

# Elasticsearch Setup (für Log Analysis & Search)
echo "🔍 Setting up Elasticsearch on port $ELASTICSEARCH_PORT..."
sudo docker run -d \
  --name ki-agent-elasticsearch \
  --restart unless-stopped \
  -e "discovery.type=single-node" \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  -e "xpack.security.enabled=false" \
  -p $ELASTICSEARCH_PORT:9200 \
  -p 9301:9300 \
  -v /opt/ki-agent/data/elasticsearch:/usr/share/elasticsearch/data \
  elasticsearch:8.11.0

echo "⏳ Waiting for databases to initialize..."
sleep 30

echo "✅ Database infrastructure setup complete!"
echo "📍 Connection details:"
echo "  PostgreSQL: localhost:$POSTGRES_PORT"
echo "  Redis: localhost:$REDIS_PORT"
echo "  Qdrant: localhost:$QDRANT_PORT"
echo "  MongoDB: localhost:$MONGO_PORT"
echo "  Elasticsearch: localhost:$ELASTICSEARCH_PORT"

# Database Schema Initialization
echo "🗄️ Initializing database schemas..."