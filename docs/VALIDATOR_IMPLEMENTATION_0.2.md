# Experimentelle Validator-Implementierung 0.2

**Sprachen:** Deutsch · [English](VALIDATOR_IMPLEMENTATION_0.2.en.md)

## Status und Abgrenzung

Dieses Dokument beschreibt den ausführbaren Python-Prototyp
`rpf-validator 0.2.0.dev0`. Seine Schema-Kennungen sind:

| Vertrag | Kennung |
| --- | --- |
| Eingabe | `rpf-validator-input-0.2` |
| Ergebnis | `rpf-validator-result-0.2` |

Die Implementierung ist **experimentell und nicht normativ**. Sie setzt die
[Validator-Operationalisierung](VALIDATOR_OPERATIONALIZATION.md) in
deterministische Regeln um, verändert aber weder `ARCHIVED_SPEC_1.2` noch
`ARCHIVED_RPF-X_IR_0.2`.

Ein `PASS` bestätigt ausschließlich, dass die bereitgestellte Prozessbeschreibung
die implementierten Regeln erfüllt. Es bestätigt weder die Wahrheit einer
Aussage noch die fachliche, rechtliche, moralische oder praktische Richtigkeit
einer Handlung.

## Öffentliche Python-API

Ein vollständig konstruiertes und strukturell gültiges `ValidatorInput` wird
mit `evaluate` geprüft:

```python
from rpf_validator import evaluate, to_json

result = evaluate(case)
print(to_json(result))
```

`case` ist dabei ein unveränderliches `ValidatorInput`-Objekt. Eine
JSON-Eingabedatei, ein JSON-Schema und ein Kommandozeilenprogramm gehören noch
nicht zu Version 0.2.

## Ausführungsvertrag

1. Die Dataklassen prüfen Typen, Wertebereiche, eindeutige Kennungen und
   Querverweise bereits beim Erzeugen des Eingabeobjekts.
2. `evaluate` arbeitet ohne Netzwerkzugriff, Sprachmodell, Zufall, Dateizugriff
   oder Systemuhr. Zeitwerte stammen ausschließlich aus der Eingabe.
3. A1 ist ein Kompetenz-Gate. Bei `INSUFFICIENT` oder `UNKNOWN` lautet das
   Ergebnis `DELEGATE`; A2–A4 und P1–P4 werden als `NOT_EVALUATED`
   protokolliert.
4. Bei ausreichender Kompetenz werden alle acht Regeln in stabiler Reihenfolge
   A1–A4 und P1–P4 ausgegeben.
5. Der Gesamtstatus folgt ausschließlich der dokumentierten Priorität:

   ```text
   STOP > DELEGATE > NO_REFERENCE > WARN > PASS
   ```

6. Alle ausgelösten Regelergebnisse bleiben erhalten, auch wenn ein höher
   priorisierter Status den Gesamtstatus bestimmt.

## Deterministische Regelsemantik in 0.2

| Regel | Aktuelle technische Prüfung | Prozesseinfluss |
| --- | --- | --- |
| A1 | Übernimmt den deklarierten Kompetenzstatus; der Validator misst Kompetenz nicht selbst. | `INSUFFICIENT` oder `UNKNOWN` → `DELEGATE`. |
| A2 | `C_i` und `C_e` bleiben getrennte Felder. Ein numerisches `C_e` ohne Evidenzquelle erzeugt ein Signal. Ein Abstand wird nur bei ausdrücklich erklärter Vergleichbarkeit und konfigurierter Schwelle geprüft; ausgelöst wird bei `abs(C_i - C_e) > threshold`. | Signal → `WARN`; keine Wahrheitsentscheidung. |
| A3 | Mindestens eine harte Iterations-, Zeit- oder Ressourcengrenze muss vorhanden sein. Erreichte Grenzen werden mit inklusiven Vergleichen (`≤` beziehungsweise `≥`) geprüft und gemeinsam ausgegeben. | Fehlende oder erreichte Grenze → `STOP`. |
| A4 | Die konfigurierte Mindestzahl an Zeithorizonten muss vorhanden und für jede Kandidatenhandlung abgedeckt sein. Nur ein Konflikt der ausgewählten Handlung mit einer deklarierten harten Grenze stoppt den Lauf. | Unvollständige Horizonte → `WARN`; harter Konflikt → `STOP`. |
| P1 | Bei Konflikt oder Revision benötigt ein identifizierter Referenzrahmen mindestens Klasse und Geltungsbereich. | Fehlend → `NO_REFERENCE`; mehrdeutig → `WARN`. |
| P2 | Eine nichtleere Unsicherheitsliste oder eine ausdrückliche Begründung für ihre Leere gilt als explizite Unsicherheit. | Leere Liste ohne Begründung → `WARN`. |
| P3 | Reflexive Läufe benötigen eine harte Terminierungsgrenze und eine Rekursionstiefengrenze. `recursion_depth >= max_recursion_depth` beendet den Lauf. | Fehlende oder erreichte Grenze → `STOP`. |
| P4 | Die Prüfung gilt für eine ausgewählte Handlung bei mindestens zwei expliziten Hypothesen. Eine irreversible Auswahl ohne eigene Auswahlbegründung erzeugt ein Signal. | Signal → `WARN`; harter Konflikt → `STOP`. |

## Auswahl einer Handlung

Version 0.2 ergänzt zwei optionale Eingabefelder:

- `selected_action_id` verweist auf genau eine vorhandene Kandidatenhandlung.
- `selection_rationale` begründet die konkrete Auswahl und ist von der
  allgemeinen Beschreibung der Kandidatenhandlung getrennt.

Eine Auswahlbegründung ohne ausgewählte Handlung ist ein technischer
Eingabefehler. Eine irreversible Auswahl darf dagegen ohne Begründung formal
repräsentiert werden, damit P4 sie als `IRREVERSIBLE_ACTION_UNJUSTIFIED`
ausgeben kann.

## Neutraler End-to-End-Fall

Der automatisierte Wetterfall enthält zwei voneinander abweichende Prognosen,
zwei Hypothesen, gesetzte Abbruchgrenzen, zwei Zeithorizonte, ausgewiesene
Restunsicherheit und die reversible Auswahl „Regenschirm mitnehmen“.

Er ergibt reproduzierbar:

```text
overall_status = PASS
A1 = SATISFIED
A2 = SATISFIED
A3 = SATISFIED
A4 = SATISFIED
P1 = SATISFIED
P2 = SATISFIED
P3 = NOT_APPLICABLE
P4 = SATISFIED
```

Dieser Test sagt nicht voraus, ob es regnen wird. Er bestätigt nur die
Regelkonformität der beschriebenen Vorgehensweise.

## Prüfstand

Version 0.2 wird durch 37 automatisierte Tests abgedeckt. Darunter befinden
sich die Mindestfälle für:

- Kompetenzdelegation und A1-Gating,
- getrennte Kalibrierung und konfigurierbare Divergenz,
- Informationsgewinn-, Iterations-, Zeit- und Ressourcengrenzen,
- Statuspriorität bei mehreren gleichzeitigen Signalen,
- fehlende und mehrdeutige Referenzrahmen,
- explizite Restunsicherheit,
- Zeithorizonte und harte deklarierte Grenzen,
- Reflexionstiefe und Reversibilität,
- identische Ergebnisse bei identischen Eingaben.

## Bekannte Grenzen

- Der Validator überprüft nicht, ob Eingabewerte, Kompetenzangaben oder
  Herkunftsnachweise sachlich zutreffen.
- Es gibt noch keinen Parser für nicht vertrauenswürdige JSON-Eingaben.
- Es gibt keine universelle Nutzenfunktion und keine automatische
  Handlungsauswahl.
- Freitextbegründungen werden auf Vorhandensein, nicht auf inhaltliche Qualität
  geprüft.
- Die maschinenlesbaren Reason-Codes sind sprachneutral; die erzeugten
  Freitextbegründungen sind derzeit englisch.
- Die Implementierung ist kein Autorisierungs-, Medizin-, Diagnose- oder
  Therapiesystem und keine empirische Bestätigung der RPF.

## Nächster technischer Schnitt

Für eine spätere Version 0.3 bieten sich ein versionierter JSON-Parser, ein
öffentliches Beispielszenario und ein Kommando wie
`rpf validate scenario.json` an. Erst danach sollte der ausführbare
RPF-Zustandsautomat angebunden werden.
