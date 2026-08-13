# Axiome und abgeleitete Prinzipien

Die vier Kernaxiome gehören zum eingefrorenen Architekturstand von RPF v1.2. Die anschließend aufgeführten Prinzipien präzisieren ihre Anwendung, ohne eine neue Version zu behaupten.

## A1 — Kompetenzaxiom

Vor epistemischer Kalibrierung wird die Passung von Kompetenz und Problemraum geprüft. Bei unzureichender Passung wird externe Expertise oder Evidenz eingeholt (`DELEGIERT`). Zusätzliche interne Konfidenz ersetzt keine Kompetenz.

## A2 — Axiom der dualen Kalibrierung

Interne Konfidenz (`C_i`) und externe Evidenz (`C_e`) werden getrennt repräsentiert. Eine hohe Ausprägung der einen Größe darf nicht stillschweigend als hohe Ausprägung der anderen ausgegeben werden.

## A3 — Terminierungsaxiom

Die Prüfung endet, wenn der marginale Informationsgewinn die relevante Schwelle nicht mehr überschreitet oder eine harte Grenze für Iterationen, Zeit oder Ressourcen erreicht ist.

```text
Stop(RPF) ⇔ (ΔK ≤ ε) ∨ (n ≥ n_max) ∨ (T ≥ T_max) ∨ (B ≤ B_min)
```

## A4 — Axiom temporaler Adaptivität

Die Bewertung einer Interpretation oder Handlung berücksichtigt Nutzen und Kosten über mehrere Zeithorizonte. Unmittelbare Stabilität oder Entlastung ist nicht automatisch gleichbedeutend mit langfristiger Adaptivität.

## Abgeleitetes Prinzip P1 — Referenzrahmen vor Revision

Ein Informationskonflikt wird vor einer globalen Wissensrevision nach seiner Ebene klassifiziert. Perspektive, Präferenz, Konvention, Mehrdeutigkeit und statistische Ausnahme sind nicht automatisch logische Widersprüche.

## Abgeleitetes Prinzip P2 — Explizite Unsicherheit

Unsicherheit ist ein zulässiger Zustand und ein zulässiges Ergebnis. Fehlende Information darf nicht durch erfundene Präzision verdeckt werden.

## Abgeleitetes Prinzip P3 — Beobachtungsbegrenzung

Selbstbeobachtung und Reflexion unterliegen denselben Anforderungen an Informationsgewinn, Ressourcen und Terminierung wie andere Prüfprozesse. RPF-X/IR konkretisiert dieses Prinzip.

## Abgeleitetes Prinzip P4 — Reversibilität

Wenn mehrere Interpretationen plausibel bleiben, werden reversible und verhältnismäßige Handlungen gegenüber irreversiblen, stark bindenden Handlungen bevorzugt. Dieses Prinzip ist eine redaktionelle Operationalisierung der adaptiven Kalibrierung und keine empirisch validierte Entscheidungsregel.
