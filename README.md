# POST BOT

## Architecture

```mermaid
graph TD
  A[Extract Tweets and References] -->|API Call| B[Twitter API]
  B --> C{References in Tweets}
  C -->|Extract| D[Tweet Text]
  C -->|Extract| E[Tweet Media]
  C -->|Extract| F[GitHub Repos]
  C -->|Extract| G[PDFs]
  C -->|Extract| H[HTML Content]
  
  F --> F1[Extract README files]
  F --> F2[Extract Repo Descriptions]

  G --> G1[Parse PDF Text]
  H --> H1[Parse HTML Content]

  D --> I[Combine Metadata]
  E --> I
  F2 --> I
  G1 --> I
  H1 --> I

  I -->|Preprocess Data| J{Preprocessing Steps}
  J --> K1[Clean Text]
  J --> K2[Extract Features]
  J --> K3[Format for Storage]

  K1 --> L[Qdrant Vector DB]
  K2 --> L
  K3 --> L

  L --> M[Use LLM for Blog Generation]
  M --> N[Blog Posts in Defined Structure]

  subgraph Data Sources
    B
    F
    G
    H
  end

  subgraph Processing
    I
    J
    K1
    K2
    K3
    L
  end

  subgraph Output
    M
    N
  end
```

## Tasks
1. Backend: Create a agentic systems
   1. Database for saving the interaction
   2. Storage for storing the extracted tweets and metadata
   3. Database for storing vector dbs
   4. Service hosted using docker
   5. Orchestrator
2. Frontend: Create a frontend for agent interactivity for blog generation, approval ,review and scheduling and also for triggering the tweet extraction
3. 