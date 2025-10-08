docker run -d \
  --name pgvector-17 \
  -p 5433:5432 \
  -e POSTGRES_PASSWORD=pgvector \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=postgres \
  -v pgvector_data:/var/lib/postgresql/data \
  pgvector/pgvector:pg17-trixie