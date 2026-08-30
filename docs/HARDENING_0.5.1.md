# RPF-Grenzhärtung 0.5.1

**Sprachen:** Deutsch · [English](HARDENING_0.5.1.en.md)

| Feld | Wert |
| --- | --- |
| Paketversion | `0.5.1.dev0` |
| Implementierungsstatus | nicht-normatives experimentelles Hardening-Update |
| Eingabevertrag | unverändert `rpf-validator-input-0.2` |
| Ergebnisvertrag | unverändert `rpf-validator-result-0.2` |
| Vorschlagsvertrag | unverändert `rpf-classification-proposal-0.1` |
| State-Machine-Trace | unverändert `rpf-state-machine-trace-0.1` |
| Änderung am eingefrorenen RPF-Kern | keine |

## Zweck

Version 0.5.1 schließt vier reproduzierbare Grenzfehler aus der Prüfung des
veröffentlichten 0.5-Baums. Sie ergänzt weder Provider noch Adapter,
Sprachmodell oder neue Bewertungsregel. Gültige öffentliche Fixtures behalten
ihre bisherigen Ergebnisse und Traces.

## Gehärtete Grenzen

### Ergebniskonsistenz vor dem Routing

`run_state_machine` prüft nun vor der Wahl eines Übergangsplans die
routingrelevante Konsistenz jedes `ValidatorResult`. Das Ergebnis muss genau
einen Eintrag für A1–A4 und P1–P4 enthalten, für jede Regel einen zulässigen
Status verwenden, das A1-Kompetenz-Gate einhalten und den Gesamtstatus tragen,
der sich aus der vollständigen Regelspur und der veröffentlichten Priorität
ergibt.

Ein über die direkte Python-API erzeugter Widerspruch wie
`overall_status=PASS` bei ausgelöstem A3 wird mit
`INCONSISTENT_RESULT_STATUS` abgewiesen. Diese Prüfung führt die Axiome nicht
erneut aus und beweist weder Begründungen noch Reason-Codes oder
Quellenaussagen als wahr.

### Vereinheitlichte JSON-Decoderfehler

Beide öffentlichen JSON-Parser verwenden nun einen gemeinsamen strikten
Decoder. Doppelte Schlüssel, nicht standardkonforme Konstanten, Syntaxfehler
und Wertebereichsfehler des Decoders bei extrem großen Zahlen werden zu
`InputValidationError`. Die CLI liefert deshalb auch für ein übergroßes
Integer-Token die dokumentierte maschinenlesbare Antwort
`INPUT_SCHEMA_INVALID` mit Exit-Code `2` statt eines Python-Tracebacks.

### Kanonischer textueller Medientyp

Der Python-Parser des Vorschlagsvertrags erzwingt nun dieselbe Form für
`media_type`, die bereits das JSON-Schema veröffentlicht: `text/<subtype>` mit
kleingeschriebenem `text`-Präfix, genau einem nicht leeren Subtyp, ohne
Leerraum und ohne weiteren Schrägstrich. Werte wie `text/`, `TEXT/PLAIN` und
`text/plain/extra` werden einheitlich abgelehnt.

### UTF-8-bündige Evidenzfragmente

Start- und exklusiver End-Offset jedes Evidenzfragments müssen jetzt auf einer
UTF-8-Zeichengrenze liegen, auch wenn der optionale `excerpt` fehlt. Der
passende Digest eines Bytebereichs, der ein Mehrbytezeichen zerschneidet, macht
diesen Bereich nicht länger zulässig.

## Kompatibilität

Keine öffentliche Datenvertragskennung wurde geändert. Das Update weist
absichtlich Objekte ab, die nach veröffentlichtem Schema oder
Evaluator-Semantik bereits ungültig waren, aber eine Python-Grenze passieren
konnten. Nutzer solcher fehlerhaften Objekte müssen sie korrigieren; für die
schema-gültigen öffentlichen Beispiele ist keine Migration nötig.

## Prüfstand und Grenze

Der Gesamtprüfstand umfasst nun 114 automatisierte Tests. Neue
Regressionstests prüfen widersprüchliche und unvollständige Ergebnisspuren, das
A1-Gate, übergroße JSON-Integer über beide Parser und die CLI,
Parser-/Schema-Gleichlauf beim Medientyp sowie fehljustierte UTF-8-Fragmente
ohne Auszug.

Dies ist ein gezieltes Hardening-Update, kein formaler Sicherheitsbeweis und
kein vollständiger Penetrationstest.
