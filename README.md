# Memoria Scholae — Research That Remembers 🧠🌐

**Repository:** `yourusername/memoria-scholae`
**Tagline:** Multi-Agent Research Orchestra combining **MemMachine** (persistent memory) + **Neo4j** (knowledge graph) + **LangGraph** (stateful agent orchestration) to turn ephemeral research sessions into durable, queryable knowledge and cross-domain hypotheses.


---

# Table of contents

1. # Overview & goals
2. # Repository layout (what’s in this repo)
3. # Architecture (high-level, components & data flow)
4. # Data model (MemMachine + Neo4j)
5. # Quickstart — local dev (Docker Compose)
6. # Configuration files (`.env`, MemMachine, Neo4j snippets)
7. # Seeder / mock data (scripts + container)
8. # LangGraph orchestration — workflow & examples
9. # Neo4j schema & multi-hop Cypher recipes (novelty scoring)
10. # Kubernetes deployment & seeder Job (manifests)
11. # CI / GitHub Actions (seed + tests)
12. # Observability, security & production guardrails
13. # Troubleshooting & FAQ
14. # Repro / deploy checklist (one page)
15. # License, credits & next steps

---

# 1 — Overview & goals

**Problem:** research knowledge is ephemeral — readings, notes, and ideas live in dispersed places (PDFs, notebooks, slack), causing lost context and missed cross-domain breakthroughs.

**Solution:** Memoria Scholae uses a 6-agent orchestra to:

* persist episodic/semantic/procedural memory in **MemMachine** (fast semantic recall),
* index structured concepts and relationships in **Neo4j** (multi-hop discovery),
* orchestrate agents with **LangGraph** to synthesize hypotheses, validate, and produce publication-ready output with provenance and HITL gates.

**Target outcomes**

* Cross-session recall (e.g., "recall my AlphaFold notes from Mar 10").
* Graph-native bridge discovery (1–7° multi-hop).
* Actionable hypotheses with confidence and traceable provenance.

---

# 2 — Repository layout (what’s in this repo)

```
memoria-scholae/
├── backend/
│   ├── agents/
│   │   ├── pi_agent/
│   │   ├── literature_agent/
│   │   ├── critic_agent/
│   │   ├── synthesizer_agent/
│   │   ├── hypothesis_agent/
│   │   └── writer_agent/
│   ├── api/                     # FastAPI app + REST glue
│   ├── memmachine/              # MemMachine client helpers
│   ├── neo4j/                   # Neo4j client wrappers and Cypher templates
│   └── langgraph/               # LangGraph workflows & runners
├── frontend/
│   ├── src/
│   │   ├── components/          # Neo4jGraph.tsx, AgentOrchestra.tsx etc.
│   │   └── pages/
├── infra/
│   ├── docker-compose.yml
│   ├── k8s/                     # deployment + job manifests
│   └── terraform/               # optional infra helpers
├── seeder/                      # Dockerfile + seeder.py
├── scripts/
│   ├── dev-up.sh
│   └── run-local-tests.sh
├── .github/
│   └── workflows/ci.yml
├── .env.example
├── README.md                    # ← this file
└── LICENSE
```

---

# 3 — Architecture (high-level)

```
User UI  <->  FastAPI  <->  LangGraph (state machine)
                              /    \
                     MemMachine     Neo4j
                      (vector)     (graph)
                         ^           ^
                         |           |
                    Agents (6) ---> writes/provenance
```

**Primary components**

* **Frontend (React + D3 + Framer Motion)**: Query input, live agent status WS, Neo4j graph visualization, HITL modals.
* **API (FastAPI)**: Aggregates UI requests, triggers LangGraph workflows, returns synthesis + provenance.
* **LangGraph**: Orchestrates tasks (recall → ingest → critique → synthesize → hypothesize → write) with state persistence & retry semantics.
* **MemMachine**: Persistent episodic/semantic/procedural memory (vector search + profile extraction).
* **Neo4j**: Concept nodes, paper nodes, experiments, edges with relationship types + multi-hop queries.
* **Agents**: 6 microservices or serverless functions (PI, Literature, Critic, Synthesizer, Hypothesis, Writer). Each logs outputs and writes provenance to MemMachine and Neo4j.

**Latency targets (design)**

* MemMachine recall: ~50ms
* Neo4j Cypher (1–3 hops): ~2ms
* Agent orchestration: ~2s
* End-to-end P95: ~2.8s

---

# 4 — Data model (MemMachine + Neo4j)

## MemMachine memory record (recommended JSON shape)

* `type`: `"episodic" | "semantic" | "procedural"`
* `producer`: e.g. `"user-lucylow"` or `"agent-literature"`
* `content`: raw text or structured JSON
* `timestamp`: ISO8601
* `metadata`: `{ session_id, source_url, doi, tags, confidence, duration_mins }`

**Example**

```json
{
  "type":"episodic",
  "producer":"lucylow",
  "content":"AlphaFold 3 notes: geometric priors in residue attention.",
  "timestamp":"2025-03-10T14:22:00Z",
  "metadata":{"session":"alpha-2025-03-10","tags":["alphafold","attention"],"confidence":0.82}
}
```

## Neo4j graph model (recommended)

Nodes:

* `(:Concept {name, created_at, vector_norm?})`
* `(:Paper {doi, title, year, text_hash})`
* `(:Experiment {id, metrics, params})`
* `(:Researcher {id, name})`

Relationships (12 canonical relationship types):

* `:DISCUSSES, :APPLIES_TO, :EXTENDS, :CONTRADICTS, :CITES, :BRIDGES, :IMPLEMENTS, :EVALUATES, :IMPROVES, :VALIDATES, :CHALLENGES, :SYNTHESIZES`

Relationship properties:

* `confidence` (float), `evidence_snippet` (string), `created_by` (string), `created_at` (ts)

---

# 5 — Quickstart — local dev (Docker Compose)

This quickstart will bring up **MemMachine**, **Neo4j** and the **backend** service locally.

## Prereqs

* Docker & Docker Compose
* Python 3.11 (for local dev of backend)
* Node 18+ (frontend)

## 1) Clone

```bash
git clone https://github.com/yourusername/memoria-scholae.git
cd memoria-scholae
cp .env.example .env
# Edit .env: set NEO4J_PASSWORD and any embedder key (OPENAI_API_KEY) if required
```

## 2) Start services

```bash
docker-compose up -d
# view logs
docker-compose logs -f memmachine neo4j backend
```

## 3) Seed mock data

Option A — run packaged seeder container:

```bash
docker build -t memoria-seeder ./seeder
docker run --rm --env-file .env memoria-seeder
```

Option B — run locally:

```bash
python seeder/seeder.py
```

## 4) Run backend + frontend (dev)

```bash
# backend
cd backend/api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# frontend
cd frontend
npm install
npm run dev
```

Open:

* Frontend UI: `http://localhost:3000`
* Backend API docs: `http://localhost:8000/docs`
* Neo4j Browser: `http://localhost:7474` (use `neo4j` / password in `.env`)

---

# 6 — Configuration files

## `.env.example`

```ini
# MemMachine
MEMMACHINE_BASE=http://memmachine:8080
MEMMACHINE_ORG=memoria-org
MEMMACHINE_PROJECT=memoria-project

# Neo4j (local dev) or Neo4j Aura (cloud)
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=ChangeMeLocally!

# OPTIONAL: Neo4j Aura
# NEO4J_URI=neo4j+s://<your-id>.databases.neo4j.io
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=<aura-password>

# Embedding / LLM provider (if MemMachine configured to use OpenAI)
OPENAI_API_KEY=

# App runtime
PORT=8000
```

## `docker-compose.yml` (core excerpt)

```yaml
version: "3.8"
services:
  memmachine:
    image: memmachine/memmachine:latest
    env_file: .env
    ports: ["8080:8080"]
    healthcheck: { test: ["CMD-SHELL","curl -f http://localhost:8080/health || exit 1"], interval: 10s, retries: 5 }

  neo4j:
    image: neo4j:5.12-enterprise
    environment: [ "NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}" ]
    ports: ["7474:7474","7687:7687"]
    volumes: ["neo4j-data:/data"]

  backend:
    build: ./backend/api
    env_file: .env
    depends_on: [memmachine, neo4j]
    ports: ["8000:8000"]

volumes:
  neo4j-data:
```

## Neo4j constraints (run once)

```cypher
CREATE CONSTRAINT IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (p:Paper) REQUIRE p.doi IS UNIQUE;
```

---

# 7 — Seeder / mock data (scripts + container)

The seeder posts mock episodic & semantic messages to MemMachine and verifies a simple semantic search.

## `seeder/seeder.py`

```python
#!/usr/bin/env python3
import os, time, requests, json
BASE = os.environ.get("MEMMACHINE_BASE","http://localhost:8080")
ORG = os.environ.get("MEMMACHINE_ORG","memoria-org")
PROJECT = os.environ.get("MEMMACHINE_PROJECT","memoria-project")
HEADERS = {"Content-Type":"application/json"}

def create_project():
    r = requests.post(f"{BASE}/api/v2/projects", json={"org_id":ORG,"project_id":PROJECT,"description":"Memoria demo"}, headers=HEADERS)
    print("project:", r.status_code, r.text)

def add_messages(msgs):
    r = requests.post(f"{BASE}/api/v2/memories", json={"org_id":ORG,"project_id":PROJECT,"messages":msgs}, headers=HEADERS)
    print("add:", r.status_code)
    print(json.dumps(r.json(), indent=2))

if __name__ == "__main__":
    create_project()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    messages = [
        {"content":"AlphaFold 3: geometric priors in residue attention maps.","producer":"lucylow","produced_for":"lit-agent","role":"user","timestamp":now,"metadata":{"tags":["alphafold","attention"],"confidence":0.82}},
        {"content":"Paper: Self-Attention is Geometric - excerpt: attention reflects coordinate locality.","producer":"lucylow","produced_for":"lit-agent","role":"user","timestamp":now,"metadata":{"doi":"10.000/xyz"}}
    ]
    add_messages(messages)
    q = {"org_id":ORG,"project_id":PROJECT,"query":"attention protein geometric","k":5}
    r = requests.post(f"{BASE}/api/v2/memories/search", json=q, headers=HEADERS)
    print("search:", r.status_code, json.dumps(r.json(), indent=2))
```

## Dockerfile (seeder)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY seeder.py .
RUN pip install requests
ENV MEMMACHINE_BASE=http://memmachine:8080
CMD ["python","seeder.py"]
```

---

# 8 — LangGraph orchestration — workflow & examples

LangGraph manages task dependencies and state. Below is a simplified state machine pseudocode demonstrating the core "research_query" workflow.

## pseudocode: `research_query` workflow

```python
from langgraph import StateMachine
from memmachine_client import MemMachineClient
from neo4j_client import Neo4jClient
from agents import LiteratureAgent, CriticAgent, SynthesizerAgent, HypothesisAgent, WriterAgent

sm = StateMachine("research_query")

@sm.task
def recall(query, user_id):
    mm = MemMachineClient()
    return {"recalls": mm.search(query, user_id=user_id, memory_types=["episodic","semantic"], k=12)}

@sm.task(depends_on=[recall])
def ingest(recalls):
    lit = LiteratureAgent.extract_and_index(recalls)
    Neo4jClient.bulk_upsert(lit["nodes"], lit["edges"])
    return {"lit": lit}

@sm.task(depends_on=[ingest])
def critic(lit):
    return CriticAgent.evaluate(lit)

@sm.task(depends_on=[critic])
def synthesize(lit, critic_res):
    return SynthesizerAgent.find_bridges(lit["concepts"], max_hops=5)

@sm.task(depends_on=[synthesize])
def hypothesize(bridges):
    return HypothesisAgent.generate(bridges)

@sm.task(depends_on=[hypothesize])
def write(hypo):
    return WriterAgent.render(hypo)
```

**Operational rules**

* Each task stores an episodic record in MemMachine with `inputs_sha256` and `outputs_sha256`.
* If `hypothesis.confidence < 0.85`, LangGraph routes to `human_review` state; publishing is blocked until a human approves.
* Trace ID propagation: LangGraph attaches `trace_id` to each MemMachine entry for distributed tracing.

---

# 9 — Neo4j schema & multi-hop Cypher recipes (novelty scoring)

## Basic setup

```cypher
CREATE CONSTRAINT IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (p:Paper) REQUIRE p.doi IS UNIQUE;
```

## Example upsert (node + relationship)

```cypher
MERGE (c:Concept {name:$name})
ON CREATE SET c.created_at = datetime()
RETURN c;
```

## Shortest bridge (multi-hop)

```cypher
:param c1 => 'SelfAttention'
:param c2 => 'ProteinContacts'
MATCH path = shortestPath((a:Concept {name:$c1})-[*1..5]-(b:Concept {name:$c2}))
RETURN path, length(path) AS hops
ORDER BY hops ASC
LIMIT 5;
```

## Novelty scoring (shorter paths + rarer nodes upweight)

```cypher
MATCH path=(a:Concept {name:$c1})-[rels*1..5]-(b:Concept {name:$c2})
WITH path, length(path) AS hops, [n IN nodes(path) | size((n)--())] AS degrees
WITH path, hops, apoc.coll.sum([d IN degrees | 1.0/(d+1)]) AS rarity_score
RETURN path, hops, rarity_score, (1.0/(hops+0.1) + rarity_score) AS novelty_score
ORDER BY novelty_score DESC
LIMIT 10;
```

> **Note:** `apoc` functions require APOC plugin enabled (available in enterprise / some Aura versions). If `apoc` is not available, compute degree via `size((n)--())` and aggregate using Cypher list functions.

---

# 10 — Kubernetes deployment & seeder Job

## 1) Store Neo4j credentials as Kubernetes Secret

```bash
kubectl create secret generic neo4j-aura-secret \
  --from-literal=NEO4J_URI='neo4j+s://<id>.databases.neo4j.io' \
  --from-literal=NEO4J_USER='neo4j' \
  --from-literal=NEO4J_PASSWORD='<password>' \
  -n memoria
```

## 2) Deployment snippet (memmachine + backend)

`k8s/deployment-memmachine.yaml` (see `infra/k8s/` in repo) — uses `secretKeyRef` to inject `NEO4J_*` vars.

## 3) Seeder Job (run once)

`k8s/job-seed-memmachine.yaml` runs the seeder container that points to `http://memmachine:8080` and populates the project/memories.

---

# 11 — CI / GitHub Actions (seed + tests)

Example `.github/workflows/ci.yml` (simplified):

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    env:
      MEMMACHINE_BASE: ${{ secrets.MEMMACHINE_URL }}
      NEO4J_URI: ${{ secrets.NEO4J_URI }}
      NEO4J_USER: ${{ secrets.NEO4J_USER }}
      NEO4J_PASSWORD: ${{ secrets.NEO4J_PASSWORD }}
    steps:
      - uses: actions/checkout@v4

      - name: Backend unit tests
        working-directory: backend/api
        run: |
          python -m pip install -r requirements.txt
          pytest -q

      - name: Seed remote MemMachine (integration)
        run: |
          python seeder/seeder.py
        env:
          MEMMACHINE_BASE: ${{ secrets.MEMMACHINE_URL }}
```

**Caveat:** CI seeding assumes a reachable MemMachine instance. If you want CI to provision a temporary Neo4j/Aura instance, you must add additional infra steps (Terraform or API calls) and safe teardown to avoid costs.

---

# 12 — Observability, security & production guardrails

## Observability

* **Logging**: JSON logs for every agent call: `{ task_id, agent_id, start_ts, end_ts, duration_ms, inputs_sha256, outputs_sha256 }`
* **Tracing**: OpenTelemetry traces propagated across tasks; store `trace_id` in MemMachine episodic entries.
* **Metrics**: Prometheus metrics: `memmachine_query_latency_seconds`, `neo4j_query_latency_seconds`, `agent_task_duration_seconds`, `hypothesis_confidence_histogram`.

## Security / Guardrails

* **Secrets**: Keep `NEO4J_PASSWORD`, `OPENAI_API_KEY`, and provider creds in Secret Manager / K8s Secrets (encrypted).
* **PII protection**: NER + regex scrubbing prior to write into persistent memory. Mask or redact PII automatically.
* **HITL policy**: Any hypothesis with `confidence < 0.85` triggers a review workflow; human annotator must approve before publishing.
* **Audit**: Every mutation includes `created_by`, `task_id`, and `sha256(raw_output)`. Immutable audit log stored in MemMachine (or external append-only store).
* **RBAC**: API enforces researcher / admin / viewer permissions scoped by MemMachine `org_id`/`project_id`.

---

# 13 — Troubleshooting & FAQ

**Q: MemMachine profile extraction returns no semantic results**
A: Check embedder/LLM provider keys (e.g., `OPENAI_API_KEY`) in `.env` or secret store — MemMachine needs an embedding provider configured for semantic extraction.

**Q: Neo4j connection errors with Aura**
A: Use `neo4j+s://<id>.databases.neo4j.io` and ensure outbound TLS allowed. Check driver version and network egress rules.

**Q: Cypher multi-hop queries slow or OOM**
A: Add constraints/indexes, increase instance sizing (for Aura), use `shortestPath()` and limit `max_hops`, and paginate results.

**Q: LangGraph tasks failing intermittently**
A: Ensure each agent returns consistent JSON and the LangGraph runner retries transient errors. Log inputs SHA256 for reproducibility.

---

# 14 — Repro / deploy checklist (one page)

1. Clone repo & copy `.env`:

```bash
git clone https://github.com/yourusername/memoria-scholae.git
cd memoria-scholae
cp .env.example .env
```

2. Edit `.env`: set `NEO4J_PASSWORD`, `OPENAI_API_KEY` (if used).
3. Start local stack:

```bash
docker-compose up -d
docker-compose logs -f memmachine neo4j backend
```

4. Build & run seeder:

```bash
docker build -t memoria-seeder ./seeder
docker run --rm --env-file .env memoria-seeder
```

5. Start backend & frontend (dev):

```bash
# backend
cd backend/api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# frontend
cd frontend
npm install
npm run dev
```

6. Validate end-to-end:

* Query UI: `Connect transformers + protein folding`
* Validate MemMachine recall: check MemMachine `/api/v2/memories/search` results
* Validate Neo4j: `MATCH (n) RETURN n LIMIT 25` in Neo4j Browser

---

# 15 — License, credits & next steps

**License:** MIT — see `LICENSE`.

**Credits & sponsors**

* **MemMachine** — persistent memory (Docker Hub: `memmachine/memmachine`)
* **Neo4j** — graph database & research reasoning (Neo4j Aura recommended)
* **LangGraph** — stateful orchestration for agent pipelines


