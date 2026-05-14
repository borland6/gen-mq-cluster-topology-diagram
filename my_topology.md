# IBM MQ Cluster Topology

```mermaid
flowchart TB
    subgraph CLS2["Cluster: CLS2"]
        subgraph FR_CLS2["Full Repositories"]
            QM4["QM4 (FR)<br>127.0.0.1(2414)"]
            QM5["QM5 (FR)<br>127.0.0.1(2415)"]
        end
        subgraph PR_CLS2["Partial Repositories"]
            QM6["QM6 (PR)<br>127.0.0.1(2416)"]
            QM7["QM7 (PR)<br>127.0.0.1(2417)"]
        end
        QM4 <==> QM5
        QM6 -.->|CLUSSDR: C_QM4| QM4
        QM7 -.->|CLUSSDR: C_QM5| QM5
    end
```

## 摘要

### Cluster: CLS2

- **Full Repositories (2):** QM4, QM5
- **Partial Repositories (2):** QM6, QM7

#### QM4 (FR)
- CLUSRCVR: C_QM4 @ 127.0.0.1(2414)
- CLUSSDR: C_QM5 -> 127.0.0.1(2415)

#### QM5 (FR)
- CLUSRCVR: C_QM5 @ 127.0.0.1(2415)
- CLUSSDR: C_QM4 -> 127.0.0.1(2414)

#### QM6 (PR)
- CLUSRCVR: C_QM6 @ 127.0.0.1(2416)
- CLUSSDR: C_QM4 -> 127.0.0.1(2414)

#### QM7 (PR)
- CLUSRCVR: C_QM7 @ 127.0.0.1(2417)
- CLUSSDR: C_QM5 -> 127.0.0.1(2415)

