# JSON-Schnittstelle und CLI 0.3

**Sprachen:** Deutsch · [English](JSON_CLI_0.3.en.md)

## Status und Abgrenzung

`rpf-validator 0.3.0.dev0` macht den experimentellen Validator über eine
strikte JSON-Schnittstelle und das Kommando `rpf` direkt nutzbar. Diese Version
ändert keine Bewertungsregel aus der
[Validator-Implementierung 0.2](VALIDATOR_IMPLEMENTATION_0.2.md).

Die Paketversion und die Versionen der Datenverträge sind absichtlich getrennt:

| Bestandteil | Kennung |
| --- | --- |
| Python-Paket und CLI | `0.3.0.dev0` |
| Eingabevertrag | `rpf-validator-input-0.2` |
| Ergebnisvertrag | `rpf-validator-result-0.2` |

Ein `PASS` besagt weiterhin nur, dass die bereitgestellte Prozessbeschreibung
die implementierten Regeln erfüllt. Es ist keine Bestätigung ihrer Tatsachen,
Quellen oder Handlung.

## Enthaltene Schnittstellen

| Artefakt | Funktion |
| --- | --- |
| [`parse_json`](../src/rpf_validator/parsing.py) | striktes JSON in ein unveränderliches `ValidatorInput` umwandeln |
| [JSON-Schema](../src/rpf_validator/schemas/rpf-validator-input-0.2.schema.json) | maschinenlesbare Beschreibung des Eingabevertrags |
| [`rpf validate`](../src/rpf_validator/cli.py) | eine Datei oder Standardeingabe prüfen |
| [`rpf schema`](../src/rpf_validator/cli.py) | das mitgelieferte Eingabeschema ausgeben |
| [Wetterbeispiel](../examples/weather-input-0.2.json) | öffentlicher, neutraler End-to-End-Fall |
| [Koinzidenz-Interpretation](../examples/coincidence-interpretation-input-0.2.json) | mehrdeutiger Referenzrahmen mit `WARN` |
| [Rückgespiegelte Begehrlichkeit](../examples/reflected-desire-input-0.2.json) | mehrdeutige Quelle eines Handlungsimpulses mit `WARN` |
| [Quellen-Echo](../examples/source-echo-input-0.2.json) | behauptungsbezogene Quellenmehrdeutigkeit mit `WARN` |
| [Loop-Collapse-Selbstbewertung](../examples/loop-collapse-self-input-0.2.json) | A1-Gate mit `DELEGATE` |
| [Extern dokumentierter Loop-Collapse-Mechanikfall](../examples/loop-collapse-external-input-0.2.json) | erhaltener Signalpfad mit `STOP` |

Der Parser und die CLI verwenden zur Laufzeit nur die Python-Standardbibliothek.

## Installation und Verwendung

Ab Python 3.11 kann das Paket lokal ohne Laufzeitabhängigkeiten installiert
werden:

```bash
python -m pip install --no-deps .
```

Das öffentliche Beispiel prüfen:

```bash
rpf validate examples/weather-input-0.2.json
```

Kompakte Ausgabe erzeugen oder JSON von der Standardeingabe lesen:

```bash
rpf validate examples/weather-input-0.2.json --compact
rpf validate - --compact < examples/weather-input-0.2.json
```

Das Schema ausgeben:

```bash
rpf schema
```

Ohne installiertes Konsolenskript ist dieselbe Funktion verfügbar als:

```bash
python -m rpf_validator validate examples/weather-input-0.2.json
```

## Strikte Eingabeprüfung

Vor der Auswertung prüft der Parser unter anderem:

- gültiges UTF-8-JSON ohne `NaN`, `Infinity` oder doppelte Objektschlüssel,
- bekannte, erforderliche Felder und die angegebene Schema-Kennung,
- Datentypen, Enums, Wertebereiche und nicht leere Texte,
- eindeutige Modellkennungen,
- Verweise auf Evidenzquellen, Zeithorizonte, Constraints und ausgewählte
  Handlungen.

Strukturfehler enthalten einen stabilen Reason-Code
`INPUT_SCHEMA_INVALID`, einen JSONPath-ähnlichen Pfad und eine Begründung. Das
JSON-Schema hilft Editoren und externen Werkzeugen bei der Vorprüfung. Der
Python-Parser bleibt jedoch maßgeblich, weil ein JSON-Schema nicht alle
Querverweise und Eindeutigkeitsregeln zwischen Objekten ausdrücken kann.

## Ausgaben und Exit-Codes

`rpf validate` gibt bei einer gültigen Eingabe immer ein vollständiges
`rpf-validator-result-0.2` als JSON aus.

| Exit-Code | Bedeutung |
| --- | --- |
| `0` | Eingabe wurde ausgewertet; gilt auch für `WARN`, `DELEGATE`, `NO_REFERENCE` und `STOP` |
| `2` | JSON oder Eingabemodell ist ungültig; Fehlercode `INPUT_SCHEMA_INVALID` |
| `3` | Datei konnte nicht gelesen oder als UTF-8 dekodiert werden; Fehlercode `INPUT_FILE_ERROR` |

Syntaxfehler beim Aufruf der CLI selbst, etwa ein fehlendes Unterkommando,
werden von `argparse` ebenfalls mit Exit-Code `2` und einem Nutzungshinweis
gemeldet.

## Neutraler Referenzfall

Das [Wetterbeispiel](../examples/weather-input-0.2.json) beschreibt zwei
abweichende öffentliche Prognosen, getrennte interne Konfidenz und externe
Evidenz, zwei Hypothesen, feste Terminierungsgrenzen und eine reversible
Handlung über zwei Zeithorizonte. Das erwartete Prozessergebnis ist `PASS`.

Dieser Status sagt nicht voraus, ob es regnen wird. Er zeigt nur, dass die
deklarierte Prozessbeschreibung die implementierten Regeln erfüllt und ihre
Restunsicherheit beibehält.

Zwei zusätzliche
[Loop-Collapse-Fixtures](TRANSFER_CASE_LOOP_COLLAPSE.md) bilden einen
nicht-klinischen Negativfall ab. Die Selbstbewertung endet bestimmungsgemäß
mit `DELEGATE`; der getrennte extern dokumentierte Mechanikfall endet mit
`STOP` und behält alle ausgelösten Signale in der Regelspur.

Die zusätzliche
[Koinzidenz-Interpretation](TRANSFER_CASE_COINCIDENCE_INTERPRETATION.md)
trennt persönliche Auffälligkeit von Konfidenz und externer Evidenz für eine
Kausalbehauptung. Ihre unquantifizierten Kalibrierungswerte erzeugen keine
Scheingenauigkeit; der ausdrücklich mehrdeutige Referenzrahmen erzeugt
bestimmungsgemäß `WARN`.

Der anschließende
[Transferfall zur rückgespiegelten Begehrlichkeit](TRANSFER_CASE_REFLECTED_DESIRE.md)
prüft, ob ein äußerer Reiz, eine wahrgenommene kollektive Präferenz, eine
Defizit-Zuschreibung und ein eigener Wunsch unbemerkt zu einer einzigen
Inferenz zusammenfallen. Die neutrale ausführbare Fixture lässt die Quelle des
spontanen Impulses offen und erzeugt deshalb ebenfalls `WARN`.

Der ergänzende
[Transferfall zu Quellen-Echo und Referenzrahmen-Drift](TRANSFER_CASE_SOURCE_ECHO.md)
trennt für eine atomare Zielbehauptung die Zahl der Texte von der Zahl
unabhängiger Evidenzwurzeln. Die Fixture führt deshalb nur eine synthetische
Primärbeobachtung als Evidenzquelle und lässt Claim-Äquivalenz, Ableitungskanten
und semantische Drift als Restunsicherheit offen. Der aktuelle Vertrag erkennt
diese Merkmale nicht selbst; das `WARN` stammt aus dem deklarierten
mehrdeutigen Referenzrahmen.

## Öffentliche Szenariomatrix

| Eingabe | Schwerpunkt | Führende Regelspur | Ergebnis |
| --- | --- | --- | --- |
| [Wetter](../examples/weather-input-0.2.json) | neutraler Referenzprozess | keine ausgelöste Regel | `PASS` |
| [Koinzidenz](../examples/coincidence-interpretation-input-0.2.json) | Bedeutung und Kausalität getrennt halten | P1 · `REFERENCE_FRAME_AMBIGUOUS` | `WARN` |
| [Rückgespiegelte Begehrlichkeit](../examples/reflected-desire-input-0.2.json) | Norm, Defizit und eigenen Wunsch getrennt halten | P1 · `REFERENCE_FRAME_AMBIGUOUS` | `WARN` |
| [Quellen-Echo](../examples/source-echo-input-0.2.json) | Texte, Claims und Evidenzwurzeln getrennt halten | P1 · `REFERENCE_FRAME_AMBIGUOUS` | `WARN` |
| [Loop-Selbstbewertung](../examples/loop-collapse-self-input-0.2.json) | Kompetenz-Gate | A1 · `COMPETENCE_INSUFFICIENT` | `DELEGATE` |
| [Loop-Mechanik](../examples/loop-collapse-external-input-0.2.json) | Abbruch- und Reflexivitätsgrenzen | A3/P3 · erreichte Grenzen | `STOP` |

Der `NO_REFERENCE`-Pfad ist durch Unit-Tests abgedeckt, besitzt aber noch keine
vollständige öffentliche Fixture.

## Prüfstand und Grenzen

Die Schnittstelle ist durch 63 automatisierte Tests abgedeckt. Dazu gehören
Roundtrips, ungültige und doppelte JSON-Felder, genaue Fehlerpfade,
Querverweise, Standardeingabe, kompakte Ausgabe, Schemaausgabe und CLI-Exit-Codes.

Die CLI:

- prüft keine Tatsachen oder Quellen außerhalb der Eingabe,
- erteilt keine Handlungserlaubnis,
- ist kein Sicherheits-, Medizin- oder Diagnosesystem,
- lokalisiert die englischen Ergebnisbegründungen derzeit nicht,
- verändert die eingefrorenen RPF-Spezifikationen nicht.

Der nächste geplante technische Schritt ist die ausführbare Übergangslogik
des RPF-Zustandsautomaten. Kompatibilitätsregeln für spätere Vorab-Schemata
bleiben eine eigene offene Aufgabe.
