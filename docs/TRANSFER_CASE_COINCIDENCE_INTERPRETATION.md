# Nicht-klinischer Transferfall: Koinzidenz-Interpretation

**Sprachen:** Deutsch · [English](TRANSFER_CASE_COINCIDENCE_INTERPRETATION.en.md)

## Status und Zweck

Dieser Transferfall untersucht eine **synthetische** auffällige Koinzidenz als
`WARN`-Fall für den experimentellen Validator. Er ist nicht normativ, nicht
empirisch validiert und keine Erweiterung der eingefrorenen
RPF-Spezifikationen.

Die Fixture beschreibt nur, dass ein innerlich auffälliges Thema und ein
ähnlich erscheinendes äußeres Ereignis zeitlich nah beieinander bemerkt wurden.
Sie prüft, ob der Prozess persönliche Bedeutung, beobachtete Koinzidenz und
äußere Kausalität auseinanderhält.

Sie entscheidet ausdrücklich nicht:

- ob eine reale Koinzidenz zufällig oder kausal ist,
- welche persönliche Bedeutung ein reales Ereignis besitzt,
- ob Gedanken ein äußeres Ereignis verursacht haben,
- ob die Wahrnehmung oder Interpretation einer realen Person angemessen ist.

Der Fall ist weder ein psychologischer Test noch ein medizinisches oder
diagnostisches Modell.

## Die entscheidende Trennung

Eine auffällige Koinzidenz kann subjektiv bedeutsam sein. Diese Bedeutsamkeit
ist jedoch nicht automatisch eine Messung der Konfidenz in eine äußere
Kausalbehauptung und auch keine externe Evidenz für diese Behauptung.

| Größe | Bedeutung in der Fixture | Umsetzung |
| --- | --- | --- |
| subjektive Auffälligkeit | warum die Beobachtung persönlich relevant erscheint | Text in Beobachtung und Referenzrahmen; kein Score |
| interne Konfidenz `C_i` | Sicherheit in eine genau benannte Kausalbehauptung | `null`, weil Behauptung und Skala nicht ausreichend bestimmt sind |
| externe Evidenz `C_e` | Stärke nachvollziehbarer äußerer Evidenz für dieselbe Behauptung | `null`, weil keine solche Evidenz deklariert ist |
| Ereigniswahrscheinlichkeit | Häufigkeit eines vorher definierten Ereignisses unter einem Modell | nicht als `C_e` umgedeutet; statistischer Kontext bleibt offen |
| Restunsicherheit | offene Kausal-, Statistik- und Rahmenfragen | drei strukturierte Unsicherheitsobjekte |

`C_e` ist im aktuellen Vertrag kein Ersatz für die Wahrscheinlichkeit eines
Ereignisses. Eine statistische Einordnung würde mindestens eine vorher
definierte Ereignisklasse, ein Beobachtungsfenster, die Zahl der Gelegenheiten
oder eine Basisrate und ein passendes Modell benötigen. Die Fixture erfindet
diese Angaben nicht.

## Ausführbare Modellierung

Die
[Koinzidenz-Fixture](../examples/coincidence-interpretation-input-0.2.json)
deklariert drei noch nicht zusammengeführte Referenzrahmenklassen:

- `SUBJECTIVE_PERCEPTION` für die persönliche Auffälligkeit,
- `OBJECTIVE_MEASUREMENT` für die protokollierte zeitliche Koinzidenz,
- `STATISTICAL_EXCEPTION` als offene statistische Einordnungsfrage.

Der Referenzrahmen bleibt deshalb bewusst `AMBIGUOUS`. Eine globale
Modellrevision wird nicht vorgeschlagen; der Revisionsumfang bleibt `LOCAL`.
Mehrere Hypothesen werden erhalten, ohne ihnen erfundene numerische Gewichte zu
geben.

Die ausgewählte Handlung `defer-causal-conclusion` ist reversibel: Beobachtung
und subjektive Bedeutung dürfen erhalten bleiben, während eine äußere
Kausalaussage bis zu methodisch definierter neuer Evidenz ausgesetzt wird.

## Erwartete Regelspur

```text
overall_status = WARN
A1 = SATISFIED
A2 = SATISFIED
A3 = SATISFIED
A4 = SATISFIED
P1 = SIGNAL    · REFERENCE_FRAME_AMBIGUOUS
P2 = SATISFIED
P3 = NOT_APPLICABLE
P4 = SATISFIED
```

A2 ist erfüllt, weil interne Konfidenz und externe Evidenz getrennt und mit
Begründung als unquantifiziert erhalten bleiben. Der Validator erzeugt keine
Scheingenauigkeit und vergleicht nicht subjektive Auffälligkeit mit äußerer
Evidenz.

Das `WARN` stammt ausschließlich aus P1. Es bedeutet: Der für eine
Kausalinterpretation erforderliche Referenzrahmen ist noch mehrdeutig. Es
verneint weder die Beobachtung noch ihre persönliche Bedeutung und bestätigt
keine der offenen Kausalhypothesen.

## Ausführung

Nach lokaler Installation:

```bash
rpf validate examples/coincidence-interpretation-input-0.2.json
```

Der Befehl endet technisch mit Exit-Code `0`, weil `WARN` ein gültiges
Validator-Ergebnis und kein Eingabefehler ist.

## Historischer Begriff und methodische Grenze

C. G. Jung veröffentlichte 1952 unter dem Begriff *Synchronizität* eine
philosophisch-psychologische Deutung bedeutungsvoller Koinzidenzen als
„akausales Verknüpfungsprinzip“. Der technische Name der Fixture bleibt
absichtlich neutral. Die historische Bezeichnung ist Kontext, keine
wissenschaftliche Bestätigung und keine Annahme des Validators.

Für eine statistische Untersuchung von Koinzidenzen sind Datenerhebung,
Ereignisdefinition und Wahrscheinlichkeitsmodell eigenständige methodische
Aufgaben. Der Validator führt diese Untersuchung nicht durch; er bewahrt ihre
fehlenden Voraussetzungen als Restunsicherheit.

Weiterführender Kontext:

- [C. G. Jung: *Synchronicity: An Acausal Connecting Principle*](https://doi.org/10.2307/j.ctt7s94k.8)
- [Persi Diaconis und Frederick Mosteller: *Methods for Studying Coincidences*](https://doi.org/10.1080/01621459.1989.10478847)

Die Quellen erläutern die historische Idee beziehungsweise statistische
Untersuchungsmethoden. Sie validieren weder RPF noch die synthetische Fixture.
