# Referenzrahmenklassifikation

## Erweiterungshypothese

Eine mögliche Erweiterung der Referenzpunkt-Funktion besteht darin, dass sie nicht ausschließlich Wahrscheinlichkeiten oder Plausibilitäten bewertet, sondern zunächst den **Referenzrahmen eines Informationskonflikts** bestimmt.

Die RPF würde somit nicht unmittelbar fragen:

> „Welche Aussage ist wahr?“

sondern zunächst:

> **„Auf welcher Ebene entsteht der scheinbare Widerspruch?“**

Dadurch soll verhindert werden, dass widersprüchliche Informationen vorschnell zur Revision eines gesamten Wissensmodells führen.

## Prinzip

Nicht jeder Widerspruch ist tatsächlich ein Widerspruch. Aussagen können lediglich unterschiedlichen Referenzebenen angehören.

| Referenzrahmen | Leitfrage | Typische Folge |
| --- | --- | --- |
| objektive Messung | Wurde dasselbe Merkmal unter vergleichbaren Bedingungen gemessen? | Quellen und Messbedingungen prüfen |
| subjektive Wahrnehmung | Beschreiben Beteiligte unterschiedliche Erlebnisse desselben Sachverhalts? | Perspektiven getrennt erhalten |
| individuelle Präferenz | Wird Gefallen oder Ablehnung als allgemeine Tatsache formuliert? | Aussage auf Person und Kontext begrenzen |
| statistische Ausnahme | Widerlegt ein Einzelfall eine Verteilung oder gehört er zu ihr? | Verteilung statt Absolutheit modellieren |
| kulturelle Bewertung | Beruht die Aussage auf einer sozialen Norm oder Konvention? | kulturellen Kontext kennzeichnen |
| sprachliche Mehrdeutigkeit | Werden gleiche Wörter in verschiedener Bedeutung verwendet? | Begriffe operationalisieren |
| tatsächlicher logischer Widerspruch | Können beide Aussagen unter denselben Voraussetzungen zugleich gelten? | Evidenzgewichtet revidieren |

## Meta-Klassifikation

Vor einer Wissensrevision kann ein Informationskonflikt zusätzlich als eine der folgenden Ursachen gekennzeichnet werden:

- Messfehler,
- Perspektivwechsel,
- subjektive Präferenz,
- kulturelle Bewertung,
- sprachliche Mehrdeutigkeit,
- statistische Ausnahme,
- tatsächlicher Widerspruch.

Mehr als eine Klasse darf gleichzeitig offenbleiben. Die Klassifikation ist selbst eine Hypothese und muss mit einer Konfidenz- und Unsicherheitsangabe verbunden werden.

## Neutraler Anwendungsfall

Zwei Wetterdienste geben unterschiedliche Regenwahrscheinlichkeiten an. Eine vorschnelle Verarbeitung könnte dies als Widerspruch behandeln. Die Referenzrahmenklassifikation prüft stattdessen Ort, Zeitraum, Aktualisierungszeit, Datenbasis, Modell und Rundung.

Mögliche Ausgabe:

```text
Klasse: Modell-/Messperspektive, kein bestätigter logischer Widerspruch
C_i: niedrig bis mittel
C_e: mittel, Quellen bleiben uneinheitlich
Revision: keine globale Revision
Handlung: robuste, kostengünstige Vorsorge
Restunsicherheit: ausdrücklich erhalten
```

## Forschungsfrage

Kann die vorgeschaltete Klassifikation von Referenzrahmen unnötige oder maladaptive Wissensrevisionen unter Unsicherheit reduzieren?

Diese Frage ist offen. Die vorliegende Architektur liefert keine empirische Antwort.
