# Architecture Decision Records (ADR) - CITMS 3.6

This document records the key architectural decisions made during the development of CITMS 3.6.

## 1. Zero-Password RustDesk Integration

**Status:** Accepted

**Context:**
The IT staff needs to remotely access managed assets (PCs, Servers) for support. Standard remote desktop solutions require manual password entry, which is inefficient and poses security risks (password sharing, weak passwords).

**Decision:**
Implement a "Zero-Password" integration with a self-hosted RustDesk server. The CITMS application will generate short-lived, one-time access tokens (OTAT) for remote sessions.

**Consequences:**
- **Pros:** Improved security (no static passwords), better user experience (one-click access), full audit trail of remote sessions.
- **Cons:** Requires a custom RustDesk relay/server setup and API integration.

---

## 2. Pessimistic Locking Strategy

**Status:** Accepted

**Context:**
Multiple IT staff members may attempt to edit the same asset or ticket simultaneously. Optimistic locking (using version numbers) can lead to "lost updates" or frustrating "conflict" messages after the user has already spent time editing.

**Decision:**
Implement a **Pessimistic Locking** strategy using Redis. When a user opens an asset for editing, a lock is acquired in Redis with a TTL (Time-To-Live). Other users will see the asset as "Locked by [User]" and will be unable to enter edit mode until the lock is released or expires.

**Consequences:**
- **Pros:** Prevents data conflicts before they happen, provides immediate feedback to users.
- **Cons:** Requires Redis as a dependency, needs a mechanism to handle "stale" locks (e.g., if a user closes the browser tab without saving).

---

## 3. FULL_REPLACE Strategy for Physical Inventory Sync

**Status:** Accepted

**Context:**
The Physical Inventory feature works offline via PWA. When a staff member performs a scan, they might be offline for hours. Upon reconnecting, the local data needs to be synchronized with the server.

**Decision:**
Adopt a **FULL_REPLACE** strategy for the inventory sync process. The client sends the entire local inventory state for a specific session to the server. The server then compares this state with the current database and updates the records accordingly, treating the client's data as the "source of truth" for that specific inventory window.

**Consequences:**
- **Pros:** Simplifies conflict resolution for offline-first scenarios, ensures data consistency for bulk inventory updates.
- **Cons:** Higher bandwidth usage for large inventory sets, requires careful handling of concurrent syncs from different devices.

---

## 4. Sentry + Prometheus + Grafana Monitoring Stack

**Status:** Accepted

**Context:**
CITMS 3.6 is a mission-critical system for IT operations. We need real-time visibility into errors, performance bottlenecks, and infrastructure health.

**Decision:**
Implement a multi-layered monitoring stack:
- **Sentry:** For application-level error tracking and performance profiling (APM).
- **Prometheus:** For collecting time-series metrics from the Node.js API and the PostgreSQL database.
- **Grafana:** For visualizing Prometheus metrics in real-time dashboards.

**Consequences:**
- **Pros:** Comprehensive visibility, proactive alerting, faster root-cause analysis.
- **Cons:** Increased infrastructure complexity and resource usage.

---

## 5. Ansible-based Deployment and Configuration Management

**Status:** Accepted

**Context:**
Manual deployment is error-prone and difficult to scale. We need a repeatable, automated way to deploy CITMS 3.6 to various environments (Dev, Staging, Production).

**Decision:**
Use **Ansible** for all deployment and configuration management tasks. Ansible playbooks will handle server provisioning, Docker container orchestration, and environment variable configuration.

**Consequences:**
- **Pros:** Infrastructure as Code (IaC), repeatable deployments, easy scaling.
- **Cons:** Requires Ansible knowledge and maintenance of playbooks.
