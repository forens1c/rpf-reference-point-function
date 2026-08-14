# Beiträge und Revisionen

Diskussion, Kritik und reproduzierbare Prüfungen sind willkommen. Die Archivdateien selbst bleiben jedoch eingefroren.

## Geeignete Beiträge

- begriffliche Kritik mit konkreter Fundstelle,
- Vorschläge für klarere Operationalisierung,
- Gegenbeispiele und bekannte Fehlermodi,
- Vorschläge für empirische Validierung,
- formale Analysen der Terminierungs- und Kalibrierungsregeln,
- sprachliche oder barrierebezogene Verbesserungen außerhalb des normativen Archivkerns.

## Archivregel

Die Kennungen `ARCHIVED_SPEC_1.2` und `ARCHIVED_RPF-X_IR_0.2` bezeichnen eingefrorene Fassungen. Inhaltliche Änderungen werden nicht unter diesen Kennungen eingepflegt. Stattdessen wird eine neue Draft-Version eröffnet und im Änderungsprotokoll begründet.

## Bearbeitete Dokumentationsfassungen

Aufgrund der Dokumentationslizenz `CC BY-NC-SA 4.0` müssen öffentliche
Bearbeitungen der Dokumentation:

1. Björn · frenetik.B angemessen nennen,
2. die Veränderung ausdrücklich kennzeichnen,
3. nichtkommerziell bleiben,
4. unter derselben oder einer kompatiblen Lizenz veröffentlicht werden,
5. eine eigene Versionskennung verwenden.

## Beiträge zum experimentellen Code

Der Python-Code, zugehörige Tests und mit einer `Apache-2.0`-SPDX-Kennung
versehene technische Konfigurationsdateien stehen unter der separaten
[Apache License 2.0](LICENSE-CODE). Sofern ein Beitrag nicht ausdrücklich als
„Not a Contribution“ gekennzeichnet wird, wird er nach den Bedingungen dieser
Softwarelizenz zur Aufnahme in das Projekt eingereicht.

Codebeiträge müssen die nicht-normative Trennung zwischen eingefrorener
Spezifikation und experimenteller Implementierung erhalten. Neue Schwellenwerte
oder Statusregeln sind als Implementierungsentscheidungen zu dokumentieren und
dürfen nicht stillschweigend als kanonische RPF-Regeln ausgegeben werden.

Vor einem Pull Request sollen mindestens die lokalen Tests ausgeführt werden:

```bash
python -m pip install --no-deps .
python -m unittest discover -s tests -v
```

## Claims

Beiträge dürfen das Modell ohne entsprechende Daten nicht als wissenschaftlich, empirisch oder klinisch validiert darstellen. Hypothesen, Beobachtungen und Ergebnisse sind deutlich voneinander zu trennen.
