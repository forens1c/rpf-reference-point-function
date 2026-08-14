# Experimentelle Validator-Operationalisierung für A1–A4 und P1–P4

**Sprachen:** Deutsch · [English](VALIDATOR_OPERATIONALIZATION.en.md)

## Status und Zweck

Dieses Dokument ist eine **nicht-normative Operationalisierung** für den ersten
deterministischen RPF-Validator. Es übersetzt A1–A4 und P1–P4 in prüfbare
Eingaben, Regeln, Ausgaben und Testfälle, ohne `ARCHIVED_SPEC_1.2` oder
`ARCHIVED_RPF-X_IR_0.2` zu verändern.

Der Validator bewertet die Nachvollziehbarkeit und Regelkonformität eines
Verfahrens. Er entscheidet weder, ob eine Aussage objektiv wahr ist, noch ob
eine Handlung außerhalb der ausdrücklich bereitgestellten Regeln moralisch,
rechtlich oder fachlich richtig ist.

Alle Skalen, Schwellenwerte und Prioritätsregeln in diesem Dokument sind
Entwurfsentscheidungen für den Prototyp. Sie müssen konfigurierbar und in jeder
Ausgabe nachvollziehbar bleiben.

## Grundlegende Trennung

Die Operationalisierung folgt dem experimentellen Prinzip der
[Trennung von Fähigkeit und Kalibrierung](CAPABILITY_CALIBRATION_SEPARATION.md):

```text
Kompetenzpassung ≠ interne Konfidenz ≠ externe Evidenz
                  ≠ Referenzrahmenpassung ≠ zeitliche Adaptivität
```

Der Validator darf diese Größen nicht zu einem einzigen Vertrauenswert
verschmelzen. Insbesondere darf hohe Kompetenz oder Konfidenz allein keinen
`PASS`-Status erzeugen.

## Zweistufiges Ergebnismodell

### Technische Eingabeprüfung

Fehlende Pflichtfelder, ungültige Wertebereiche oder widersprüchliche
Datentypen erzeugen `INPUT_ERROR`. Das ist ein technischer Validierungsfehler
vor Ausführung der RPF-Regeln und kein RPF-Ergebnis.

Fachlich unbekannte Angaben müssen dagegen durch ausdrücklich zulässige Werte
wie `UNKNOWN` oder `null` sowie einen Grund repräsentiert werden können. Damit
bleiben „formal ungültig“ und „inhaltlich noch unbekannt“ unterscheidbar.

### Regelergebnisse

Jede Regel erhält ein eigenes Ergebnis:

| Regelstatus | Bedeutung |
| --- | --- |
| `SATISFIED` | Die für den Fall erforderliche Regel wurde nachvollziehbar erfüllt. |
| `SIGNAL` | Die Regel erzeugt ein Kalibrierungs- oder Vorsichtssignal. |
| `TRIGGERED` | Eine vorgesehene Schutz- oder Terminierungsregel wurde ausgelöst. |
| `NOT_APPLICABLE` | Die Regel ist für den konkreten Fall nicht anwendbar. |
| `NOT_EVALUATED` | Eine vorherige Ausstiegsbedingung verhindert die weitere Prüfung. |

`TRIGGERED` bedeutet nicht automatisch, dass ein Axiom verletzt wurde. Eine
korrekte Delegation oder Terminierung ist gerade die beabsichtigte Wirkung der
Regel.

### Zusammenfassender Prozessstatus

| Prozessstatus | Bedeutung |
| --- | --- |
| `PASS` | Alle erforderlichen Regeln wurden geprüft; der Prozess darf mit ausgewiesener Restunsicherheit fortfahren oder ausgeben. |
| `WARN` | Der Prozess ist ausführbar, enthält aber ein offenes Kalibrierungs-, Evidenz- oder Verhältnismäßigkeitssignal. |
| `DELEGATE` | Kompetenzpassung ist unzureichend oder für die erforderliche Aufgabe nicht belegbar. |
| `NO_REFERENCE` | Ein erforderlicher Referenzrahmen konnte nicht belastbar bestimmt werden. |
| `STOP` | Eine harte Terminierungsbedingung oder eine zuvor deklarierte Grenze wurde ausgelöst. |

Für den ersten Prototyp gilt die deterministische Priorität:

```text
STOP > DELEGATE > NO_REFERENCE > WARN > PASS
```

Die Priorität bestimmt nur den zusammenfassenden Status. Alle ausgelösten
Regelergebnisse und Begründungen bleiben in der Ausgabe erhalten. Sie ist keine
allgemeine Rangfolge von Gefährlichkeit oder Bedeutung.

## Minimales Eingabemodell

| Feld | Minimaler Inhalt | Verwendung |
| --- | --- | --- |
| `schema_version` | Versionskennung des Eingabeschemas | reproduzierbare Interpretation der Felder |
| `case_id` | stabile Fallkennung | Protokollierung und Testreproduzierbarkeit |
| `observation` | Inhalt, Herkunft und optionaler Zeitpunkt | Trennung von Beobachtung und Interpretation |
| `problem_domain` | benannter Aufgaben- oder Wissensbereich | Kompetenzprüfung A1 |
| `competence` | `SUFFICIENT`, `INSUFFICIENT` oder `UNKNOWN`; Begründung und Herkunft | A1 und `DELEGATE` |
| `calibration` | `C_i`, Begründung von `C_i`, `C_e`, Evidenzquellen und Begründung von `C_e` | A2 und P2 |
| `conflict` | Konflikt vorhanden; vorgeschlagener Revisionsumfang `NONE`, `LOCAL` oder `GLOBAL` | P1 |
| `reference_frame` | Status, Klasse, Geltungsbereich, Annahmen und deklarierte Grenzen | P1 und Referenzrahmenpassung |
| `hypotheses` | unterscheidbare Hypothesen mit Evidenzbezügen | P1, P2 und P4 |
| `termination` | `ΔK`, `ε`, Iteration, Iterationsgrenze, Zeit und Ressourcenbudget | A3 und P3 |
| `time_horizons` | mindestens zwei benannte Horizonte mit erwarteten Folgen | A4 |
| `candidate_actions` | Handlungsoptionen, Folgen je Horizont, Reversibilität und Begründung | A4 und P4 |
| `residual_uncertainty` | offene Fragen, fehlende Information und verbleibende Alternativen | P2 und Ausgabe |
| `validator_config` | Schwellenwerte, Skalen, harte Grenzen und deren Kennungen | reproduzierbare Regelanwendung |

Für den Prototyp dürfen `C_i` und `C_e` als Werte von `0.0` bis `1.0`
repräsentiert werden. Diese gemeinsame technische Skala macht die Größen nicht
inhaltlich identisch. Jeder Wert benötigt eine getrennte Begründung. `C_e` ist
eine deklarierte Einschätzung der Evidenzstärke und kein vom Validator
berechneter Wahrheitswert.

Ein numerischer Abstand wie `abs(C_i - C_e)` darf nur als konfiguriertes Signal
verwendet werden, wenn Skala, Schwelle und Vergleichbarkeit ausdrücklich
festgelegt sind. RPF definiert keinen universellen Drift-Grenzwert.

## Operationalisierungsmatrix

| ID | Erforderliche Eingaben | Deterministische Prüfung | Regelergebnis und Einfluss |
| --- | --- | --- | --- |
| **A1 Kompetenz** | `problem_domain`, `competence.status`, Begründung und Herkunft | A1 wird vor epistemischer Bewertung geprüft. `INSUFFICIENT` oder `UNKNOWN` öffnen keine weitere fachliche Bewertung. | `TRIGGERED` → `DELEGATE`; nachfolgende fachliche Regeln können `NOT_EVALUATED` sein. `SUFFICIENT` mit Begründung → `SATISFIED`. |
| **A2 Duale Kalibrierung** | getrennte Objekte für `C_i` und `C_e`, jeweilige Begründung, Evidenzquellen, Skalenkennung | Prüfen, ob Konfidenz und Evidenz strukturell sowie semantisch getrennt dokumentiert sind. Eine konfigurierte Abweichung erzeugt ein Signal, keinen automatischen Fehler. | Formal gültige, aber nicht nachvollziehbar getrennte oder begründete Angaben → `SIGNAL` und mindestens `WARN`. Nachvollziehbare Trennung → `SATISFIED`; eine Abweichung bleibt als Reason-Code sichtbar. |
| **A3 Terminierung** | `ΔK`, `ε`, `n`, `n_max`, `T`, `T_max`, `B`, `B_min` | Vor jeder weiteren Iteration prüfen: `(ΔK ≤ ε) ∨ (n ≥ n_max) ∨ (T ≥ T_max) ∨ (B ≤ B_min)`. Grenzen müssen vor dem Lauf feststehen. | Erfüllte Abbruchbedingung → `TRIGGERED` und `STOP` mit genauem Grund. Vollständige, noch nicht erreichte Grenzen → `SATISFIED`. Ausdrücklich fehlende harte Grenzen → `TRIGGERED` und `STOP`. |
| **A4 Temporale Adaptivität** | mindestens zwei `time_horizons`; Folgen jeder relevanten Handlung; deklarierte harte Grenzen | Prüfen, ob kurzfristige und spätere Folgen getrennt betrachtet wurden. Der Validator berechnet ohne externe Bewertungsregel keinen universellen Gesamtnutzen. | Fehlender Mehrhorizontvergleich → `SIGNAL` und `WARN`. Konflikt mit deklarierter harter Grenze → `TRIGGERED` und `STOP`. Vollständiger Vergleich → `SATISFIED`. |
| **P1 Referenzrahmen vor Revision** | `conflict`, `reference_frame.status`, Klasse, Geltungsbereich, Annahmen, `revision_scope` | Bei Konflikt oder Modellrevision muss die Referenzrahmenprüfung vor einer globalen Revision protokolliert sein. Mehrere Klassen dürfen offenbleiben. | Fehlender erforderlicher Rahmen → `TRIGGERED` und `NO_REFERENCE`. Mehrdeutiger Rahmen bei ausgesetzter globaler Revision → `SIGNAL` und `WARN`. Bestimmter Rahmen → `SATISFIED`. |
| **P2 Explizite Unsicherheit** | `residual_uncertainty`, fehlende Information, Begründung einer gegebenenfalls leeren Liste | Prüfen, ob Unsicherheit im Ergebnis ausdrücklich erhalten bleibt. Eine leere Liste ist nur mit Begründung zulässig. | Fehlende oder verdeckte Restunsicherheit → `SIGNAL` und `WARN`. Ausgewiesene Unsicherheit → `SATISFIED`. |
| **P3 Beobachtungsbegrenzung** | Kennzeichen für Reflexion/Selbstbeobachtung, Rekursionstiefe und dieselben Zeit-, Iterations- und Ressourcengrenzen wie A3 | Bei reflexiven Läufen müssen Tiefe und Abbruchgrenzen vor jeder weiteren Selbstprüfung kontrolliert werden. | Kein reflexiver Lauf → `NOT_APPLICABLE`. Fehlende oder erreichte Grenze → `TRIGGERED` und `STOP`. Kontrollierter reflexiver Lauf → `SATISFIED`. |
| **P4 Reversibilität** | plausible Hypothesen, `candidate_actions`, Reversibilität, Rücknahmekosten und Auswahlbegründung | Wenn mehrere Hypothesen plausibel bleiben, muss eine reversible und verhältnismäßige Option berücksichtigt werden. Irreversible Auswahl benötigt eine ausdrückliche Begründung. | Unbegründete irreversible Auswahl trotz verfügbarer reversibler Option → `SIGNAL` und `WARN`; Konflikt mit harter Grenze → `STOP`. Nachvollziehbare Auswahl → `SATISFIED`. |

## Stabile Reason-Codes des ersten Prototyps

Reason-Codes sollen maschinenlesbar sein und nicht von der Ausgabesprache
abhängen.

| Regel | Reason-Code | Typischer Prozessstatus |
| --- | --- | --- |
| Eingabe | `INPUT_SCHEMA_INVALID` | `INPUT_ERROR` |
| A1 | `COMPETENCE_INSUFFICIENT` | `DELEGATE` |
| A1 | `COMPETENCE_UNKNOWN` | `DELEGATE` |
| A2 | `CALIBRATION_NOT_SEPARATED` | `WARN` |
| A2 | `CONFIDENCE_EVIDENCE_DIVERGENCE` | `WARN` |
| A3 | `INFORMATION_GAIN_LIMIT` | `STOP` |
| A3 | `ITERATION_LIMIT` | `STOP` |
| A3 | `TIME_LIMIT` | `STOP` |
| A3 | `RESOURCE_LIMIT` | `STOP` |
| A3/P3 | `TERMINATION_BOUND_MISSING` | `STOP` |
| A4 | `TIME_HORIZON_MISSING` | `WARN` |
| A4 | `DECLARED_CONSTRAINT_CONFLICT` | `STOP` |
| P1 | `REFERENCE_FRAME_MISSING` | `NO_REFERENCE` |
| P1 | `REFERENCE_FRAME_AMBIGUOUS` | `WARN` |
| P2 | `UNCERTAINTY_NOT_REPORTED` | `WARN` |
| P3 | `REFLEXIVE_DEPTH_LIMIT` | `STOP` |
| P4 | `IRREVERSIBLE_ACTION_UNJUSTIFIED` | `WARN` |

Weitere Reason-Codes benötigen eine dokumentierte Schemaänderung. Freitext
ergänzt die Codes, ersetzt sie aber nicht.

## Minimaler Ausgabevertrag

```json
{
  "schema_version": "rpf-validator-result-0.1",
  "case_id": "example-001",
  "overall_status": "WARN",
  "rule_results": [
    {
      "rule_id": "A2",
      "status": "SIGNAL",
      "reason_codes": ["CONFIDENCE_EVIDENCE_DIVERGENCE"],
      "rationale": "Internal confidence exceeds declared external evidence."
    }
  ],
  "residual_uncertainty": ["Independent source remains unavailable."],
  "next_step": "Recalibrate or obtain additional external evidence.",
  "config_id": "prototype-defaults-0.1"
}
```

Die Ausgabe muss zusätzlich die verwendeten Eingaben beziehungsweise deren
stabile Referenzen, die ausgelösten Grenzen und die Konfiguration ausweisen.
`PASS` bedeutet ausschließlich, dass der dokumentierte Prozess die
implementierten Regeln erfüllt hat.

## Mindesttestmatrix

| Test-ID | Eingabesituation | Erwartetes Ergebnis |
| --- | --- | --- |
| `SCHEMA-01` | `C_i = 1.2` bei Skala `0.0…1.0` | `INPUT_ERROR` mit `INPUT_SCHEMA_INVALID`; keine RPF-Regel ausführen |
| `A1-01` | Kompetenz `INSUFFICIENT` | `DELEGATE`; A2, P1 und weitere fachliche Prüfungen nicht als verletzt ausgeben |
| `A1-02` | Kompetenz `UNKNOWN` ohne belegbare Herkunft | `DELEGATE` mit `COMPETENCE_UNKNOWN` |
| `A2-01` | `C_i` und `C_e` verwenden dasselbe ungetrennte Feld | mindestens `WARN` mit `CALIBRATION_NOT_SEPARATED` |
| `A2-02` | hohes `C_i`, niedriges `C_e`, getrennt und nachvollziehbar | `WARN` als Kalibrierungssignal, kein automatischer Wahrheitsentscheid |
| `A3-01` | `T ≥ T_max` | `STOP` mit `TIME_LIMIT`; A3 gilt als regelgerecht ausgelöst |
| `A3-02` | Terminierungsobjekt formal gültig, aber alle harten Grenzen ausdrücklich ungesetzt | `STOP` mit `TERMINATION_BOUND_MISSING` |
| `A4-01` | nur unmittelbarer Zeithorizont vorhanden | mindestens `WARN` mit `TIME_HORIZON_MISSING` |
| `P1-01` | globale Revision vorgesehen, Referenzrahmen fehlt | `NO_REFERENCE`; keine globale Revision freigeben |
| `P2-01` | Ergebnis enthält kein Feld für Restunsicherheit | `WARN` mit `UNCERTAINTY_NOT_REPORTED` |
| `P3-01` | reflexiver Lauf erreicht maximale Rekursionstiefe | `STOP` mit `REFLEXIVE_DEPTH_LIMIT` |
| `P4-01` | irreversible Handlung gewählt, reversible Option vorhanden, keine Begründung | mindestens `WARN` mit `IRREVERSIBLE_ACTION_UNJUSTIFIED` |
| `FLOW-01` | alle erforderlichen Dimensionen geprüft; Restunsicherheit bleibt sichtbar | `PASS`; Unsicherheit darf weiterhin ungleich null sein |
| `PRIORITY-01` | gleichzeitig A2-Signal und A3-Zeitlimit | Gesamtstatus `STOP`; beide Regelergebnisse bleiben erhalten |

## Neutraler End-to-End-Akzeptanzfall

Der erste vollständige Test verwendet den bestehenden Wetterfall:

1. Zwei Wetterdienste melden unterschiedliche Regenwahrscheinlichkeiten für
   denselben Nachmittag.
2. Die Kompetenzpassung für das Lesen der veröffentlichten Prognosen wird mit
   Begründung als ausreichend deklariert.
3. `C_i` und `C_e` werden getrennt einschließlich ihrer Herkunft angegeben.
4. Der Referenzrahmen wird als Prognose- beziehungsweise Modellperspektive
   klassifiziert; Ort, Zeitraum und Aktualisierungszeit werden abgeglichen.
5. Mehrere Wetterhypothesen bleiben offen.
6. Zeit-, Iterations- und Ressourcengrenzen sind vorab gesetzt.
7. Eine kostengünstige reversible Handlung, beispielsweise das Mitführen eines
   Schirms, wird über mindestens zwei Zeithorizonte bewertet.
8. Die verbleibende Prognoseunsicherheit wird ausgegeben.

Erwartetes Ergebnis ist `PASS`, sofern alle Prozessregeln erfüllt sind. Dieser
Status behauptet nicht, dass Regen oder Trockenheit wahr vorhergesagt wurde.

## Nicht-Ziele

Diese Operationalisierung ist insbesondere:

- kein Wahrheitsdetektor,
- keine universelle Nutzenfunktion,
- keine automatische Autorisierung für Handlungen,
- kein Personen-, Intelligenz- oder Kompetenzranking,
- kein medizinisches, psychologisches oder diagnostisches Instrument,
- keine empirische Bestätigung der RPF.

## Offene Implementierungsentscheidungen

Vor dem ersten Code-Release bleiben mindestens folgende Punkte ausdrücklich
offen:

- Weiterentwicklungs- und Kompatibilitätsregeln für das initiale typisierte
  Datenmodell und die Paketstruktur,
- Standardkonfiguration und Benennung der Schwellenwerte,
- Umgang mit teilweise fehlenden, aber nicht zwingenden Eingaben,
- formale Repräsentation deklarierter Grenzen,
- Serialisierung und Versionsstrategie der Ein- und Ausgabeschemata.
