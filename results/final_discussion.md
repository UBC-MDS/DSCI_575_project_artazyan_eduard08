# Final Discussion

## Step 1: Improve Your Workflow

### Dataset Scaling

- **Number of products (records) used:** We combined roughly **275,000** review records and **50,000** product-metadata records, merged on **`parent_asin`**. After an **inner join** and preprocessing, the usable dataset contained **over 10,000** valid records, which we used to rebuild the semantic (FAISS) and BM25 indices and to run the RAG pipeline.
- **Changes to sampling strategy (if any):** We did **not** apply a separate random sample on top of the join. The **inner join** acts as a filter: only rows with both review and metadata are kept, which **reduces** size versus a full outer merge and **removes** incomplete rows. There was no additional stratified or down-sampling step beyond this merge and preprocessing.

### LLM Experiment

- **Models compared (name, family, size)**
  - **Meta-Llama-3-8B-Instruct** — Meta, Llama 3 family, **8B** parameters
  - **Qwen3-8B** — Alibaba, Qwen family, **8B** parameters  

  These two were chosen to compare different LLM families under the **same** RAG pipeline, retrieval, and top‑k context.

- **Results and discussions**
  - **Prompt used (copy it here):**

    "You are a helpful Amazon shopping assistant. Answer the question using ONLY the provided context (product reviews and metadata). Only include information that directly answers the question. Do NOT mention unrelated products. If the context does not contain enough relevant information, say so clearly. Cite the product ASIN when possible."

  - **Results:** We evaluated both models on **5 queries**. For each query, retrieval was fixed (**same** top‑k documents, **same** context, **same** prompt) so differences reflected **model behavior** only. Llama’s answers were **more concise and coherent**, stayed within the **provided context**, and **clearly** said when context was insufficient. Qwen produced **longer** outputs, often with **intermediate reasoning** (e.g. `<think>`-style content), which made answers **less direct** and sometimes **off-topic** relative to the user’s question.

- **Which model you chose and why:** We selected **Meta-Llama-3-8B-Instruct** because it showed **stronger grounding**, **better instruction-following**, and **more consistent** RAG-appropriate behavior than Qwen in this setting.

---

## Step 2: Additional Feature (state which option you chose)

**Option:** **Cloud deployment** — a **public, hosted** Streamlit app (Additional Feature: fully deployed application).

### What You Implemented

- **Description of the feature:** A **fully deployed** Streamlit **query dashboard** (same **Search** and **RAG** ideas as locally: BM25 vs semantic search; semantic or hybrid RAG with LLM answers), hosted on **Streamlit Community Cloud** so users can try the system **without** cloning the repo or building indices locally.
- **Key results or examples:** The live app is available at **<https://kindle-review-rag-engine.streamlit.app/>**. It demonstrates end-to-end **retrieval + generation** in a **browser**, validating that the pipeline can run in a **managed** environment with **secrets** (e.g. Hugging Face API token) configured on the host.

---

## Step 3: Improve Documentation and Code Quality

### Documentation Update

- Summary of **`README`** improvements: Added **Milestone 3** content (**LLM comparison**, **final model choice**), **clarified** conda/env setup and how to run **notebooks** and the **Streamlit** app, documented **`HUGGINGFACEHUB_API_TOKEN`**, and added a line pointing to the **deployed** Streamlit URL as the **additional feature**.

### Code Quality Changes

- Summary of **cleanups** / quality work: **Docstrings** on custom functions where appropriate, **relative paths only** (no hardcoded absolute paths in code), **no API keys in source** (use **`.env`** / environment variables), and general **readability** pass consistent with the rest of the project.

---

## Step 4: Cloud Deployment Plan

*Required subsections: data storage (raw and processed), vector and BM25 indices, how indices are loaded and persisted, compute and concurrency, LLM inference approach, new-review ingestion and re-indexing strategy, and brief architectural justification.*

This section describes how we would run the Kindle RAG / search system in a **production** cloud environment. The current prototype uses a Streamlit app with local `data/processed/` files and Hugging Face’s hosted **Inference API** for the LLM; the plan below generalizes that into a durable, scalable design.

### Architecture overview

At a high level: **ingestion and batch jobs** write raw and processed data and pre-built **indices to object storage**; **stateless app servers** (or a managed Streamlit/container host) load indices into memory at startup or refresh from a shared cache; a **load balancer** routes user traffic; **LLM calls** go to a managed inference API to avoid undifferentiated heavy lifting on GPUs.

### 1. Data storage (raw and processed)

| Data | Proposed location | Rationale |
|------|-------------------|-----------|
| **Raw** reviews and metadata (e.g. JSON/parquet as delivered by upstream) | **Object storage** (e.g. Amazon S3, Google Cloud Storage, or Azure Blob) in a *raw* prefix, with lifecycle rules for cost (e.g. infrequent access tier after 30 days) | Object storage is **durable, cheap at rest**, and fits append-only or periodic dumps of catalog-scale data. It avoids tying large files to a single VM disk and supports reprocessing from an immutable source of truth. |
| **Processed** merged table (`merged.parquet` and derived columnar files) | Same cloud account, **separate** *processed* prefix or bucket, **versioned** by pipeline run (e.g. `processed/2025-11-20/merged.parquet`) | Keeps a **reproducible** snapshot for each index build; rollback is trivial. Columnar Parquet is efficient for ETL and for optional serverless query engines (Athena, BigQuery external tables) if we add analytics later. |

We **do not** store raw or processed “truth” data only on application instances: that would be lost on scale-in and complicates backups.

### 2. Vector (FAISS) and sparse (BM25) indices: storage and hosting

- **FAISS index** (`.index` + `semantic_meta.json` or equivalent) and **BM25** (`bm25.pkl` and associated vocabulary): treat these as **versioned build artifacts** in **object storage** (same *artifacts* or *indices* prefix), keyed by build id or content hash, e.g. `indices/build-abc123/semantic_faiss.index`, `bm25.pkl`.
- **Rationale:** Indices are **large binaries**; object storage offers **low cost per GB**, high durability, and the ability to serve the same files to many regions or blue/green deploys. They are not a good fit for a transactional database.

Optionally, for **very low-latency** first-byte reads within one region, a **managed cache** (e.g. ElastiCache, Memorystore) could hold *hot* embedding metadata, but the canonical store remains object storage so restarts and new nodes always pull a consistent version.

### 3. How indices are loaded and persisted between sessions

- **Between user sessions:** The data in object storage is **persistent**; it does not disappear when a user closes a browser.
- **Between application instances / restarts:** Each app worker is **stateless** on disk: on **startup** (or on a **config change**), it downloads the **current** index bundle from object storage to **local SSD** (e.g. `/tmp` or an ephemeral container volume), then `mmap`s or loads FAISS and unpickles BM25 into **RAM** for fast retrieval.
- **Rationale for RAG / search:** **In-memory (or memory-mapped) indices** keep **p50/p95 query latency** low for similarity and BM25—critical for a **recommendation- and Q&A–style** tool where users expect sub-second retrieval before the LLM call.

When we deploy a **new** index version, we update a **small manifest** (e.g. `indices/current.txt` pointing to `build-xyz`) so new containers pull the new bundle; old workers drain or are replaced in a rolling deploy.

This is **not** dynamic re-indexing on every request; it is **load-once per process** with **periodic** or **on-demand** index refreshes (see below).

### 4. Compute, concurrency, and LLM inference

#### 4.1 Application hosting environment

- **Prototype / light traffic:** **Streamlit Community Cloud** (as in our additional feature) or **similar PaaS** is acceptable: simple deploy from Git, secrets for `HUGGINGFACEHUB_API_TOKEN`, minimal ops.
- **Production** with SLOs and more control: run the app as a **container** on **Amazon ECS (Fargate)**, **Google Cloud Run**, or **Azure Container Apps**—or **Kubernetes** if we need custom autoscaling and sidecars. The container image bundles Python + Streamlit (or a thin **FastAPI** wrapper if we split UI from API).
- **Rationale:** Containers give **repeatable** environments, integrate with **secrets managers**, and scale **horizontally** behind a **load balancer** (ALB, Cloud Load Balancing, Application Gateway).

#### 4.2 Concurrent users

- **Retrieval (BM25 + FAISS):** FAISS and BM25 lookups are **read-only** and **thread-safe** for shared read-only data structures if implemented carefully, or we default to **one process per vCPU** with a **replicated** index in each (simplest). Under load, we **scale out** replicas: each replica holds a copy of the in-memory index (or mmap), and the **load balancer** distributes **round-robin** or by least connections.
- **LLM calls:** The **bottleneck** is usually **inference**, not vector search. We cap **concurrent** upstream calls per worker (semaphore) and rely on the **provider’s** queueing and rate limits, or we add a **client-side** queue and backoff to avoid overwhelming the API. For bursty traffic, a **message queue** (SQS, Pub/Sub) with async “answer by notification” is an option but changes UX.
- **Rationale for a product-like recommender:** **Horizontal scaling of stateless app tiers** is standard: cost grows with **concurrent** users; **managed** LLM APIs avoid provisioning **GPU** pools for 8B-class models.

#### 4.3 LLM inference strategy: managed API vs. self-hosted GPU

| Approach | When we would use it | Trade-offs |
|----------|----------------------|------------|
| **Managed API** (e.g. **Hugging Face Inference Endpoints** or **Serverless**), as in this project | **Default for production** aligned with the current code path | **Pros:** No GPU operations team, pay **per request/token**, automatic scaling of inference replicas, model updates on the provider side. **Cons:** Ongoing **API** cost, **vendor** dependency, data leaves VPC unless we use **private** endpoints. |
| **Self-hosted** on **GPU** instances (G5, A100) with **TGI** or **vLLM** | If **strict data residency**, **very high** volume (negotiate $/token), or **custom fine-tunes** that vendors do not host | **Pros:** Full control, **no** per-call markup for heavy usage. **Cons:** **CapEx/OpEx** for GPU idle time, **ops** burden (health checks, autoscaling GPU pools), and **slower** iteration than API updates. |

For this project’s **RAG over public-style reviews** and **Meta-Llama-3-8B-Instruct**, the **managed endpoint** is the best fit: it matches our milestone implementation and **keeps the retrieval layer** the focus of in-house engineering.

### 5. Real-time updates and new reviews

- **Source of new reviews:** In production, new rows would arrive via **batch exports** (e.g. daily from a data lake), **change-data-capture** from an operational DB, or **streamed** events (Kinesis, Kafka) into a **staging** area in object storage.
- **Mechanism to incorporate new reviews:** A **scheduled** or **event-triggered** pipeline (Airflow, Cloud Composer, Step Functions, or a **container job**) runs: **merge** new reviews with existing metadata → **rebuild** document text → **recompute** BM25 and **re-embed** new/changed chunks → **write** a new FAISS index and `bm25.pkl` → **register** a new `build_id` in the manifest.
- **Dynamic vs. batch re-indexing:** For **recommendation and search quality**, **periodic batch re-indexing** (e.g. **nightly** or **hourly** if the business needs fresher results) is the right default: it is **simpler**, **cheaper** than per-write embedding calls, and avoids **write amplification** on the vector index. **Near–real-time** (e.g. sub-minute) would require **incremental** FAISS strategies or **separate** “hot” small indices merged at query time—higher **complexity**; we would only add this if product requirements demand **live** review feedback.

### 6. Brief architectural justification (recommendation / RAG context)

- **Object storage** for raw, processed, and index **artifacts** balances **cost** (pennies/GB) and **durability**; recommendation workloads are **read-heavy** and **latency-sensitive** at query time, not on the storage API itself.
- **In-memory / mmap indices on compute** minimize **retrieval** latency, which **directly** affects perceived quality in a RAG app (users tolerate LLM seconds less if search feels instant).
- **Managed LLM** avoids running **8B-parameter** inference ourselves—appropriate when our **differentiation** is **retrieval and UX**, not **model training**.
- **Stateless app + externalized indices** supports **rollbacks**, **A/B** tests on index versions, and **blue/green** deploys without a monolithic “one server with everything on disk” failure mode.

Together, these choices form a **production-ready** path from our current **Streamlit + local artifacts + Hugging Face API** stack without requiring an unnecessary rewrite of the core retrieval code paths.
