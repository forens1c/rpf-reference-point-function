# RPF-Klassifikationsvorschlag 0.1

**Sprachen:** Deutsch · [English](CLASSIFICATION_PROPOSAL_CONTRACT_0.1.en.md)

| Feld | Wert |
| --- | --- |
| Implementierungsstatus | nicht-normativer experimenteller Vertrag |
| Paketversion | `0.5.0.dev0` |
| Vorschlagsvertrag | `rpf-classification-proposal-0.1` |
| bestehender Validator-Eingabevertrag | unverändert `rpf-validator-input-0.2` |
| bestehender Validator-Ergebnisvertrag | unverändert `rpf-validator-result-0.2` |
| bestehender State-Machine-Trace | unverändert `rpf-state-machine-trace-0.1` |
| Provider oder Adapter enthalten | nein |
| Änderung am eingefrorenen RPF-Kern | keine |

## Zweck

Der Vertrag definiert die erste maschinenlesbare Grenze für spätere optionale
Referenzrahmen-Klassifikatoren. Ein regelbasiertes Modul oder ein späteres
Sprachmodell darf Kandidaten, eigene Konfidenz, Unsicherheiten und belegende
Textstellen **vorschlagen**. Es darf kein RPF-Ergebnis festlegen.

Der Vertrag beendet den Ablauf absichtlich vor der Konstruktion eines
`ValidatorInput`:

```text
Textquelle
  → optionaler Klassifikationsanbieter
  → ClassificationProposal · rpf-classification-proposal-0.1
  → strikter Parser und Integritätsprüfung
  → Ende des implementierten 0.5-Schnitts
```

Ein späterer Adapter benötigt zusätzlich einen unabhängig bereitgestellten
Basisfall und einen eigenen Mapping-Trace. Der Vorschlag enthält nicht genug
Informationen, um Kompetenz, Kalibrierung, Hypothesen, Terminierung,
Zeithorizonte oder Handlungen zu erzeugen.

## Nicht-autorisierende Vertragsgrenze

Jeder Datensatz muss enthalten:

```json
"proposal_role": "NON_AUTHORITATIVE_SUGGESTION"
```

Der Provider darf insbesondere nicht liefern:

- `overall_status`,
- A1–A4-/P1–P4-Reason-Codes,
- Zustände, Ereignisse oder Übergänge,
- Kompetenzurteile,
- `C_i`, `C_e` oder externe Evidenzwerte,
- Handlungswahl oder Autorisierung,
- eine selbst zugewiesene Autoritätsstufe.

Unbekannte Felder werden auf jeder Objektebene abgelehnt. Die
Bewertungsautorität darf später nur aus einem vertrauenswürdigen
Aufrufkontext oder einer kontrollierten Provider-Registry stammen, nicht aus
der Ausgabe des zu bewertenden Providers. `assessment_subject_id` benennt nur
das behauptete Bewertungssubjekt; ein späterer Aufrufer muss diese Bindung
gegen seinen eigenen Auftrag prüfen.

Diese Grenze ist eine Rechte- und Kontrollgrenze, kein Wahrheitsdetektor. Ein
formal gültiger, aber semantisch falscher Vorschlag kann ohne zusätzliche
Evidenz nicht automatisch als unwahr erkannt werden.

## Datenmodell

| Bereich | Inhalt |
| --- | --- |
| `provider` | stabile Anbieterkennung und -version, Implementierungsart, Konfigurations-Digest und bei modellbasierten Anbietern Modellkennung und -version |
| `input_reference` | Fall, Bewertungssubjekt, Quellkennung, Medientyp und Digest der exakten UTF-8-Eingabe |
| `candidates` | ein oder mehrere Referenzrahmen-Kandidaten mit eigenem Status, Klassen, Scope, Begründung und Provider-Konfidenz |
| `preferred_candidate_id` | vom Provider bevorzugter Kandidat; keine Annahme oder Kernentscheidung |
| `evidence_fragments` | byte-adressierte Quellfragmente mit eigenem Digest und optionalem, begrenztem Auszug |
| `uncertainties` | strukturierte Unsicherheitspositionen und die davon betroffenen Kandidaten |
| `generated_at` | optionaler, vom Provider behaupteter RFC-3339-Zeitpunkt mit Zeitzone |

Alle Python-Modelle sind unveränderliche Dataclasses. Kandidaten-, Evidenz- und
Unsicherheitskennungen müssen eindeutig sein; Querverweise werden beim Parsen
geprüft.

## Status und Klassen bleiben getrennt

Der Kandidatenstatus verwendet ausschließlich:

- `IDENTIFIED`,
- `AMBIGUOUS`,
- `MISSING`.

Die Klassendimension verwendet weiterhin die bestehenden RPF-Klassen wie
`OBJECTIVE_MEASUREMENT`, `SUBJECTIVE_PERCEPTION` oder
`LINGUISTIC_AMBIGUITY`. Ein `MISSING`-Kandidat darf weder Klassen noch Scope
behaupten. `IDENTIFIED` und `AMBIGUOUS` benötigen mindestens eine Klasse und
einen ausdrücklich beschriebenen Scope.

## Provider-Konfidenz und Unsicherheit

`provider_confidence` ist nur die Selbstangabe des Klassifikators auf der
Skala `provider-self-report-unit-interval-0.1`. Sie ist ausdrücklich weder
interne Konfidenz `C_i` des bewerteten Prozesses noch externe Evidenz `C_e`.
Eine spätere Adapterstufe darf sie nicht stillschweigend in diese Felder
kopieren.

Restunsicherheit wird nicht zu einem globalen Risiko- oder Personenscore
verdichtet. Jeder Unsicherheitseintrag besitzt eine Beschreibung und verweist
auf die betroffenen Kandidaten.

## Integrität und Provenienz

Der Quelltext wird als exakte UTF-8-Bytefolge mit SHA-256 gebunden. Ein
Evidenzfragment enthält einen Start- und exklusiven End-Byteoffset, einen
eigenen Digest und optional einen auf 500 Zeichen begrenzten Auszug.

```python
from pathlib import Path
from rpf_validator import (
    load_classification_proposal,
    verify_source_payload,
)

proposal = load_classification_proposal(
    "examples/classification-proposal-identified-0.1.json"
)
source = Path(
    "examples/classification-source-identified.txt"
).read_text(encoding="utf-8")
verify_source_payload(proposal, source)
```

Die Prüfung bestätigt nur Byte-Integrität und Fragmentzuordnung. Ein passender
Hash bestätigt weder Wahrheit, Quellenunabhängigkeit, Qualität noch
Bewertungsautorität. Der behauptungsspezifische Provenienzgraph aus dem
[Quellen-Echo-Transferfall](TRANSFER_CASE_SOURCE_ECHO.md) bleibt deshalb eine
getrennte spätere Vertragserweiterung.

## Öffentliche neutrale Vorschläge

Die drei Dateien sind bewusst von Hand erzeugte synthetische Vertrags-Fixtures.
Die Kennung `rpf.synthetic-fixture-provider` bezeichnet keinen im Paket
implementierten Provider. Sie zeigt nur, wie die Herkunft eines späteren
regelbasierten Vorschlags gebunden werden müsste.

| Vorschlag | Demonstrierter Zustand |
| --- | --- |
| [explizite Celsius-Messung](../examples/classification-proposal-identified-0.1.json) | ein `IDENTIFIED`-Kandidat der Klasse `OBJECTIVE_MEASUREMENT` |
| [nicht definiertes Label „high“](../examples/classification-proposal-ambiguous-0.1.json) | bevorzugter `AMBIGUOUS`-Kandidat, alternative Messdeutung und strukturierte Unsicherheit |
| [zwei Anzeigen ohne Definition](../examples/classification-proposal-missing-0.1.json) | `MISSING` ohne erfundene Klasse oder Scope |

Die zugehörigen Textquellen liegen separat im Verzeichnis `examples/`. Dadurch
können vollständiger Payload-Digest, Bytebereiche, Fragment-Digests und
Auszüge gemeinsam geprüft werden.

## Negative Vertragsfälle

Der maschinenlesbare
[Negativfall-Katalog](../tests/fixtures/classification-proposal-invalid-cases-0.1.json)
prüft sechs getrennte Grenzverletzungen:

1. Einschleusen von `overall_status`,
2. selbst zugewiesene Autorität,
3. ungültiger SHA-256-Digest,
4. Verwechslung von Frame-Status und Frame-Klasse,
5. Klassenbehauptung trotz `MISSING`,
6. Einschleusen von Provider-Konfidenz als `external_evidence`.

Weitere Tests decken doppelte Kennungen, unbekannte Querverweise, falsche
Quell- und Fragment-Digests, nicht standardkonforme JSON-Zahlen, doppelte
JSON-Schlüssel, unzulässige Modellmetadaten sowie Zeitangaben ohne Zeitzone ab.

## JSON-Schema und Python-API

Das gebündelte Draft-2020-12-Schema kann ausgegeben werden:

```bash
rpf schema --contract classification-proposal
```

Der öffentliche Parser erzeugt noch kein Validator-Ergebnis:

```python
from rpf_validator import parse_classification_proposal_json

proposal = parse_classification_proposal_json(source_json)
```

## Noch nicht implementiert

Version 0.5 enthält absichtlich:

- keinen tatsächlich klassifizierenden Provider,
- keinen Provider-Auftragsvertrag oder vertrauenswürdige Registry,
- keinen Adapter zum `ValidatorInput`,
- keine automatische Semantikanalyse,
- keine Änderung an Evaluator oder Zustandsautomat,
- keine automatische Prüfung faktischer Wahrheit.

Der nächste sinnvolle Schnitt ist ein einfacher, deterministischer
regelbasierter Provider. Erst danach sollte ein Adapter mit einer expliziten
Feld-Allowlist, Bindungsprüfung und eigenem Mapping-Trace entworfen werden. Ein
Sprachmodell bleibt eine spätere austauschbare Provider-Implementierung.

## Prüfstand

Der 0.5-Schnitt erhöht den Gesamtprüfstand auf 105 automatisierte Tests. Die
neuen Tests prüfen Modelle, Parser, Schema, drei öffentliche Vorschläge,
Integritätsbindung und die beschriebenen Negativgrenzen unter Python 3.11 oder
neuer.
