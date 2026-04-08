# CITMS 3.6 Architecture Documentation (C4 Model)

This document provides a high-level overview of the CITMS 3.6 (IT Asset Management System) architecture using the C4 model.

## 1. System Context Diagram

The System Context diagram shows the CITMS system and its interactions with external users and systems.

```mermaid
C4Context
    title System Context Diagram for CITMS 3.6

    Person(admin, "IT Administrator", "Manages IT assets, tickets, and system configurations.")
    Person(staff, "IT Staff", "Performs physical inventory and handles support tickets.")
    Person(user, "End User", "Submits support tickets and views assigned assets.")

    System(citms, "CITMS 3.6", "Centralized IT Asset Management System.")

    System_Ext(rustdesk, "RustDesk Server", "Self-hosted remote desktop server for asset control.")
    System_Ext(sentry, "Sentry", "Error tracking and performance monitoring.")
    System_Ext(prometheus, "Prometheus/Grafana", "Infrastructure and application metrics monitoring.")
    System_Ext(ldap, "Active Directory / LDAP", "External user authentication and synchronization.")

    Rel(admin, citms, "Manages assets and tickets", "HTTPS")
    Rel(staff, citms, "Performs inventory and support", "HTTPS/PWA")
    Rel(user, citms, "Submits tickets", "HTTPS")

    Rel(citms, rustdesk, "Initiates remote sessions", "Zero-Password API")
    Rel(citms, sentry, "Sends error logs", "HTTPS")
    Rel(citms, prometheus, "Exposes metrics", "HTTP/Metrics")
    Rel(citms, ldap, "Authenticates users", "LDAPS")
```

## 2. Container Diagram

The Container diagram shows the high-level technology choices and how containers communicate.

```mermaid
C4Container
    title Container Diagram for CITMS 3.6

    Person(admin, "IT Administrator", "IT Management")

    System_Boundary(citms_boundary, "CITMS 3.6") {
        Container(spa, "Single Page Application", "React, Tailwind CSS", "Provides the user interface for all users.")
        Container(pwa, "Progressive Web App", "React, Service Workers", "Enables offline physical inventory capabilities.")
        Container(api, "API Server", "Node.js, Express", "Handles business logic and data access.")
        ContainerDb(db, "Database", "PostgreSQL", "Stores asset data, tickets, and user information.")
        ContainerDb(cache, "Cache", "Redis", "Handles session management and pessimistic locking.")
    }

    System_Ext(rustdesk, "RustDesk Server", "Remote Desktop")

    Rel(admin, spa, "Uses", "HTTPS")
    Rel(spa, api, "API Calls", "JSON/HTTPS")
    Rel(pwa, api, "API Calls / Sync", "JSON/HTTPS")
    Rel(api, db, "Reads/Writes", "SQL")
    Rel(api, cache, "Locks/Sessions", "Redis Protocol")
    Rel(api, rustdesk, "Remote Control Integration", "HTTPS")
```

## 3. Component Diagram (API Server)

The Component diagram shows the internal structure of the API Server container.

```mermaid
C4Component
    title Component Diagram for API Server

    Container(spa, "Single Page Application", "React")
    
    Container_Boundary(api_boundary, "API Server") {
        Component(auth_ctrl, "Auth Controller", "Express", "Handles login, LDAP sync, and JWT.")
        Component(asset_ctrl, "Asset Controller", "Express", "Manages asset lifecycle and inventory.")
        Component(ticket_ctrl, "Ticket Controller", "Express", "Handles support ticket workflows.")
        Component(lock_svc, "Locking Service", "Node.js/Redis", "Implements Pessimistic Locking for concurrent edits.")
        Component(sync_svc, "Inventory Sync Service", "Node.js", "Handles FULL_REPLACE strategy for offline sync.")
        Component(rustdesk_svc, "RustDesk Integration", "Node.js", "Manages Zero-Password remote access tokens.")
    }

    ContainerDb(db, "PostgreSQL", "Database")
    ContainerDb(cache, "Redis", "Cache")

    Rel(spa, auth_ctrl, "Authenticates", "JSON/HTTPS")
    Rel(spa, asset_ctrl, "Manages Assets", "JSON/HTTPS")
    Rel(spa, ticket_ctrl, "Manages Tickets", "JSON/HTTPS")

    Rel(asset_ctrl, lock_svc, "Acquires Locks", "Internal")
    Rel(asset_ctrl, sync_svc, "Triggers Sync", "Internal")
    Rel(asset_ctrl, rustdesk_svc, "Requests Remote Access", "Internal")

    Rel(lock_svc, cache, "Stores Locks", "Redis")
    Rel(asset_ctrl, db, "Queries Data", "SQL")
    Rel(ticket_ctrl, db, "Queries Data", "SQL")
```
