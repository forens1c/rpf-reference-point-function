# Experimentelles Implementierungsprinzip: Trennung von Fähigkeit und Kalibrierung

**Sprachen:** Deutsch · [English](CAPABILITY_CALIBRATION_SEPARATION.en.md)

## Status

Dieses Dokument beschreibt eine **nicht-normative Designregel** für den
geplanten experimentellen RPF-Validator. Es verändert weder
`ARCHIVED_SPEC_1.2` noch `ARCHIVED_RPF-X_IR_0.2` und ist keine empirische oder
klinische Validierung der RPF.

## Kernsatz

> Fähigkeit ist nicht dasselbe wie Kalibrierung, und Kalibrierung ist nicht
> dasselbe wie die Passung eines Referenzrahmens.

Für die Implementierung gilt daher:

```text
Kompetenzpassung ≠ interne Konfidenz ≠ externe Evidenz
                  ≠ Referenzrahmenpassung ≠ zeitliche Adaptivität
```

Diese Größen können zusammenhängen, dürfen im Validator aber nicht als
Synonyme behandelt oder stillschweigend zu einem einzigen Vertrauenswert
verschmolzen werden. Hohe Fähigkeit kann auch die effiziente Verfolgung eines
ungeeigneten lokalen Ziels ermöglichen. Sie ist deshalb für sich genommen kein
Grund für `PASS`.

## Getrennte Prüfdimensionen

| Dimension | Leitfrage | Abgrenzung |
| --- | --- | --- |
| Kompetenzpassung | Reichen die aufgabenspezifischen Fähigkeiten für diese Beurteilung? | Keine Aussage über allgemeine Intelligenz oder den Wert einer Person. |
| Interne Konfidenz (`C_i`) | Wie sicher bewertet das System seine eigene Einschätzung? | Konfidenz ist weder Kompetenz noch Beweis. |
| Externe Evidenz (`C_e`) | Wie gut ist die Einschätzung durch nachvollziehbare externe Daten oder Verfahren gestützt? | Evidenz bleibt mit Herkunft, Qualität und Grenzen verbunden. |
| Referenzrahmenpassung | Sind Ziel, Ebene, Geltungsbereich und maßgebliche Randbedingungen bestimmt? | Ein technisch erreichbares Ziel ist nicht automatisch im relevanten Rahmen zulässig oder angemessen. |
| Zeitliche Adaptivität | Bleibt die Handlung über die festgelegten Zeithorizonte tragfähig? | Kurzfristiger Erfolg kann mit mittel- oder langfristigen Kosten kollidieren. |
| Reversibilität | Wie gut können Folgen bei einer Fehlannahme begrenzt oder rückgängig gemacht werden? | Reversibilität ersetzt keine Evidenz, beeinflusst aber die Verhältnismäßigkeit einer Handlung. |

## Konsequenzen für den Validator

1. Jede Prüfdimension erhält ein eigenes Feld, eine eigene Datenherkunft und
   eine eigene Begründung.
2. Ein Gesamtstatus darf nicht allein aus hoher Kompetenz oder hoher
   Konfidenz abgeleitet werden.
3. Fehlende Kompetenz soll zu `DELEGATE` führen, nicht zur Behauptung einer
   Axiomverletzung.
4. Ein fehlender oder unzureichend bestimmter Referenzrahmen soll
   `NO_REFERENCE` auslösen.
5. Eine auffällige Abweichung zwischen `C_i` und `C_e` ist zunächst ein
   Kalibrierungssignal. Sie führt zu `WARN` oder erneuter Kalibrierung, sofern
   keine zusätzliche Stoppregel greift.
6. Ein Konflikt mit vorher deklarierten Grenzen oder mit der erforderlichen
   Betrachtung mehrerer Zeithorizonte kann `STOP` auslösen.
7. `PASS` ist erst zulässig, wenn alle für den Fall erforderlichen Dimensionen
   geprüft und verbleibende Unsicherheiten ausgewiesen wurden.

Die Priorität gleichzeitig ausgelöster Zustände muss in der Implementierung
explizit und testbar festgelegt werden. Die genannten Statuszuordnungen sind
Entwurfsentscheidungen für den Prototyp und keine rückwirkende Erweiterung der
archivierten Spezifikation.

## Beispielhafte Ergebnismuster

| Befund | Beispielstatus |
| --- | --- |
| Kompetenzpassung unzureichend | `DELEGATE` |
| Hohe Kompetenz, aber Referenzrahmen fehlt | `NO_REFERENCE` |
| Hohe Konfidenz bei schwacher externer Evidenz | `WARN` |
| Lokales Ziel kollidiert mit einer deklarierten übergeordneten Grenze | `STOP` |
| Erforderliche Dimensionen geprüft, Restunsicherheit ausgewiesen | `PASS` |

Diese Muster bewerten die Regelkonformität eines Prozesses. Sie entscheiden
nicht, ob eine Aussage objektiv wahr ist.

## Sicherheits- und Anwendungsgrenze

Das Prinzip ist für die Modellierung technischer Entscheidungsprozesse gedacht.
Der experimentelle Validator darf nicht zur Bewertung, Diagnose oder
Klassifikation von Menschen, psychischen Zuständen oder substanzbezogenem
Verhalten eingesetzt werden. Analogien aus solchen Bereichen können Gedanken
veranschaulichen, sind aber kein Bestandteil der technischen Prüflogik und kein
empirischer Nachweis der RPF.

## Kandidat für eine spätere Revision

Erst Implementierung, Tests und dokumentierte Evaluation können zeigen, ob die
Trennung von Fähigkeit und Kalibrierung als eigenes Prinzip in einer zukünftigen
RPF-Version vorgeschlagen werden sollte. Bis dahin bleibt sie eine
experimentelle Implementierungsregel.
