# Ausführbarer RPF-Zustandsautomat 0.4

**Sprachen:** Deutsch · [English](STATE_MACHINE_RUNTIME_0.4.en.md)

| Feld | Wert |
| --- | --- |
| Implementierungsstatus | nicht-normativer experimenteller Prototyp |
| Paketversion | `0.4.0.dev0` |
| Eingabevertrag der Runtime | `rpf-validator-result-0.2` |
| Ausgabevertrag der Runtime | `rpf-state-machine-trace-0.1` |
| Feste Übergangsgrenze | 7 |
| Änderung am eingefrorenen RPF-Kern | keine |

## Zweck

Version 0.4 setzt den dokumentierten RPF-Zustandsraum erstmals als
ausführbare Übergangslogik um. Die Runtime nimmt ausschließlich ein bereits
erzeugtes, versioniertes `ValidatorResult` entgegen. Sie bewertet keine Axiome
erneut, interpretiert keine Texte und entscheidet nicht, ob eine Aussage wahr
ist.

```text
ValidatorInput
  → evaluate(...)
  → ValidatorResult · rpf-validator-result-0.2
  → run_state_machine(...)
  → StateMachineTrace · rpf-state-machine-trace-0.1
```

Damit bleiben Validator und Zustandsautomat getrennte Module. Ihre einzige
direkte Kopplung ist der veröffentlichte Ergebnisvertrag.

## Implementierungsform

Die Runtime verwendet eine bewusst kleine Hybridarchitektur:

- `RPFState` und `TransitionEvent` sind typsichere Enums.
- `ALLOWED_TRANSITIONS` ist eine unveränderliche deklarative Tabelle.
- `transition(state, event)` ist eine reine Funktion.
- `TransitionRecord` und `StateMachineTrace` sind unveränderliche Dataclasses.
- kein Übergangsplan darf mehr als sieben Schritte enthalten.
- jeder erfolgreiche Lauf endet wieder in `IDLE`.

Es gibt weder ein veränderliches globales Zustandsobjekt noch eine
Zustandsklasse pro Zustand. Die Tabelle bleibt dadurch direkt prüfbar und
auditierbar.

## Deklarierte Übergänge

| Ausgang | Ereignis | Ziel |
| --- | --- | --- |
| `IDLE` | `BEGIN` | `ISOLATION` |
| `ISOLATION` | `APPLY_OPERATORS` | `OPERATOR_APPL` |
| `ISOLATION` | `DELEGATE` | `DELEGIERT` |
| `ISOLATION` | `NO_REFERENCE` | `NO_REFERENCE` |
| `OPERATOR_APPL` | `EVALUATE_DELTA` | `DELTA_EVAL` |
| `DELTA_EVAL` | `GENERATE_HYPOTHESES` | `HYPOTHESIS_GEN` |
| `DELTA_EVAL` | `STOP` | `OUTPUT_INTERFACE` |
| `HYPOTHESIS_GEN` | `EVALUATE_ADAPTIVELY` | `ADAPTIVE_VAL` |
| `ADAPTIVE_VAL` | `EMIT` | `OUTPUT_INTERFACE` |
| `ADAPTIVE_VAL` | `STOP` | `OUTPUT_INTERFACE` |
| `NO_REFERENCE` | `EMIT` | `OUTPUT_INTERFACE` |
| `OUTPUT_INTERFACE` | `RESET` | `IDLE` |
| `DELEGIERT` | `RESET` | `IDLE` |

Kompetenz- und Referenzprüfung werden nicht als neue kanonische Zustände
erfunden. Ihre Ergebnisse erscheinen als explizite Übergänge aus
`ISOLATION`. So bleibt der Zustandsraum des eingefrorenen Entwurfs erhalten.

## Routing der Prozessstatus

| Validator-Ergebnis | Protokollierter Pfad |
| --- | --- |
| `PASS` oder `WARN` | `IDLE → ISOLATION → OPERATOR_APPL → DELTA_EVAL → HYPOTHESIS_GEN → ADAPTIVE_VAL → OUTPUT_INTERFACE → IDLE` |
| `DELEGATE` | `IDLE → ISOLATION → DELEGIERT → IDLE` |
| `NO_REFERENCE` | `IDLE → ISOLATION → NO_REFERENCE → OUTPUT_INTERFACE → IDLE` |
| `STOP` aus A3/P3 | `IDLE → ISOLATION → OPERATOR_APPL → DELTA_EVAL → OUTPUT_INTERFACE → IDLE` |
| `STOP` aus A4/P4 | `IDLE → ISOLATION → OPERATOR_APPL → DELTA_EVAL → HYPOTHESIS_GEN → ADAPTIVE_VAL → OUTPUT_INTERFACE → IDLE` |

Bei `STOP` bleibt das Ereignis selbst im Übergangsprotokoll sichtbar. Wenn
mehrere Stoppsignale vorliegen, beendet eine bereits in A3 oder P3 erreichte
Terminierungsgrenze den Pfad in `DELTA_EVAL`; ein späterer A4-/P4-Befund wird
nicht benötigt, um den Kontrollfluss weiterzuführen. Die vollständigen
Regelergebnisse bleiben trotzdem im vorgelagerten `ValidatorResult` erhalten.

## Kommandozeile

Ein öffentliches JSON-Szenario kann jetzt direkt durch Validator und Runtime
geführt werden:

```bash
rpf trace examples/weather-input-0.2.json
```

Kompakte Ausgabe:

```bash
rpf trace examples/wave-tank-no-reference-input-0.2.json --compact
```

Der Trace enthält unter anderem:

- seine eigene Schemafassung,
- die konsumierte Ergebnis-Schemafassung,
- Fallkennung und Prozessstatus,
- jeden nummerierten Übergang mit Quelle, Ereignis und Ziel,
- den abschließenden Zustand `IDLE`,
- die feste maximale Übergangszahl.

Die Exit-Codes bleiben von fachlichen Prozessstatus getrennt:

| Code | Bedeutung |
| --- | --- |
| `0` | gültige Auswertung und gültiger Trace, auch bei `STOP` |
| `2` | ungültige JSON-/Eingabestruktur |
| `3` | Datei- oder Dekodierungsfehler |
| `4` | technischer State-Machine-Vertragsfehler |

## Python-API

```python
from rpf_validator import evaluate, run_state_machine, to_json

result = evaluate(case)
trace = run_state_machine(result)
print(to_json(trace))
```

Ein einzelner Übergang kann unabhängig geprüft werden:

```python
from rpf_validator import RPFState, TransitionEvent, transition

next_state = transition(RPFState.IDLE, TransitionEvent.BEGIN)
assert next_state is RPFState.ISOLATION
```

Ein nicht deklarierter Übergang wird deterministisch mit
`INVALID_TRANSITION` abgelehnt. Nicht unterstützte Ergebnisverträge,
widersprüchliche `STOP`-Spuren und eine Überschreitung der festen Schrittgrenze
besitzen eigene technische Fehlercodes. Diese Codes sind bewusst nicht Teil
der fachlichen A1–A4-/P1–P4-Reason-Codes.

## Sicherheits- und Erkenntnisgrenze

Der Zustandsautomat kontrolliert den Ablauf eines bereits strukturierten
Ergebnisses. Er kann unzulässige Übergänge, nicht unterstützte Verträge und
unvollständige Stoppspuren zurückweisen. Er kann jedoch nicht feststellen, ob
plausibel und intern konsistent eingetragene Ausgangsdaten faktisch falsch
sind.

Ein späteres Sprachmodell oder Semantikmodul darf deshalb nur strukturierte
Vorschläge liefern. Herkunft, Bewertungsautorität und externe Evidenz bleiben
separat erforderlich. Die deterministische Runtime ist ein Kontrollfluss, kein
Wahrheitsdetektor und keine Autorisierungsinstanz.

## Prüfstand

Der technische Schnitt ist durch 80 automatisierte Tests abgesichert. Sie
prüfen unter anderem:

- alle fünf öffentlichen Prozessstatus,
- frühe und adaptive `STOP`-Pfade,
- unveränderliche Übergangstabelle und Traces,
- deterministische Wiederholung identischer Läufe,
- Ablehnung ungültiger Übergänge und inkonsistenter Stoppspuren,
- feste Übergangsgrenze und Rückkehr zu `IDLE`,
- `rpf trace` für normale und `NO_REFERENCE`-Szenarien.
