# Synthetischer Transferfall: Modellboot ohne Referenzdefinition

**Sprachen:** Deutsch · [English](TRANSFER_CASE_WAVE_TANK_NO_REFERENCE.en.md)

## Status und Zweck

Dieser Transferfall schließt den bisher nur durch Unit-Tests sichtbaren
`NO_REFERENCE`-Pfad mit einer vollständigen öffentlichen Fixture. Er verwendet
ein Modellboot in einem synthetischen Wellenbecken und zwei nicht dokumentierte
Anzeigen mit den Ausgaben `HIGH` und `LOW`.

Der Fall ist nicht-normativ und verändert weder die eingefrorene
RPF-Spezifikation noch den Eingabevertrag `rpf-validator-input-0.2`. Er ist kein
nautisches Modell, keine Aussage über die Stabilität realer Boote und keine
Navigations- oder Sicherheitsanweisung.

## Beobachtung und fehlender Bezug

Das Modellboot hält im Versuch dieselbe **horizontale Station**. Bei einem
synchronisierten Ablesezeitpunkt zeigen zwei Laboranzeigen:

```text
Anzeige A = HIGH
Anzeige B = LOW
```

Bekannt ist nur:

- Die horizontale Station des Modells bleibt gleich.
- Vertikale Bewegung durch die Welle ist möglich und wird nicht verneint.
- Beide Labels wurden beim selben synthetischen Ablesezeitpunkt protokolliert.
- Die Anzeigen gehören zum Testaufbau, sind aber nicht dokumentiert.

Nicht bekannt ist:

- welche Messgröße jeder Kanal erfasst,
- auf welche Achse und welchen Nullpunkt er sich bezieht,
- welche Einheit oder Schwelle hinter dem Label steht,
- ob `HIGH` und `LOW` Messwerte, Grenzklassen oder Gerätezustände bezeichnen.

Die gleiche horizontale Station stellt deshalb noch keinen gemeinsamen
Referenzrahmen für die beiden Ausgaben her.

## Warum Fachwissen die Lücke nicht automatisch schließt

Ein nautisch oder messtechnisch erfahrener Mensch kann schnell plausible
Deutungen bilden: Bootshöhe, Wellenhöhe, Tiefgang, Abstand, Wasserstand,
Schwellwert oder Gerätestatus. Diese Kompetenz verbessert die Hypothesenbildung.
Sie belegt jedoch nicht, welche Größe die konkrete Anzeige tatsächlich misst.

Der Fall unterscheidet daher:

```text
fachlich plausible Konvention
≠ dokumentierte Kanaldefinition
```

Würde ein Auswerter eine vertraute Konvention ohne Gerätebeschreibung als
gegeben einsetzen, entstünde eine **implizite Referenzrahmen-Injektion**. Das
fehlende Metadatum würde dann unbemerkt durch Vorwissen ersetzt.

Wenn später ein Sensorhandbuch oder Versuchsprotokoll Messgröße, Nullpunkt,
Einheit und Labelsemantik nachvollziehbar festlegt, muss der Datensatz erneut
bewertet werden. Das Ergebnis kann dann zu `WARN` oder `PASS` wechseln. Diese
Änderung wäre beabsichtigt und keine Instabilität des Validators.

## Abgrenzung zu `WARN`

| Zustand | Informationslage | Ergebnis |
| --- | --- | --- |
| `AMBIGUOUS` | mehrere tatsächlich belegte Referenzrahmen sind bekannt, aber noch nicht aufgelöst | `WARN` |
| `MISSING` | die Angaben zur Bildung eines Referenzrahmens fehlen | `NO_REFERENCE` |

Die möglichen nautischen oder messtechnischen Deutungen sind in dieser Fixture
nur Hypothesen. Sie sind keine belegten Referenzrahmen. Deshalb bleiben
`reference_frame.classes` leer und `reference_frame.scope` ist `null`.

## Vergleichbarkeit als Arbeitsnotiz

Für die beiden Labels müsste mindestens ein gemeinsamer Vergleichsschlüssel
bekannt sein:

```text
K = (Messgröße, Achse, Nullpunkt, Einheit, Zeitpunkt, Labelsemantik)
```

Die Schreibweise ist eine lokale Erläuterung des Transferfalls, kein neues
RPF-Axiom. In der Fixture fehlen wesentliche Bestandteile von `K`; daher wird
weder ein numerischer Evidenzvergleich noch ein logischer Widerspruch
behauptet.

## Ausführbare Modellierung

Die
[Wellenbecken-Fixture](../examples/wave-tank-no-reference-input-0.2.json)
deklariert:

- ausreichende Kompetenz nur für die strukturelle Auswertung der Eingabe,
- einen lokalen Konflikt zwischen zwei protokollierten Labels,
- unquantifizierte und ausdrücklich nicht vergleichbare `C_i`-/`C_e`-Werte,
- `reference_frame.status = MISSING`, leere Klassen und keinen Scope,
- mehrere mögliche, aber unbestätigte Kanaldeutungen,
- eine reversible Handlung: Vergleich aussetzen und Metadaten anfordern.

Die Fixture führt ein synthetisches Beobachtungsprotokoll als Quelle. Dessen
Qualitätshinweis hält genau fest, welche Kanalmetadaten nicht überliefert sind.
Der Validator prüft diese Angaben nicht außerhalb der bereitgestellten Eingabe.

## Erwartete Regelspur

```text
overall_status = NO_REFERENCE
A1 = SATISFIED
A2 = SATISFIED
A3 = SATISFIED
A4 = SATISFIED
P1 = TRIGGERED · REFERENCE_FRAME_MISSING
P2 = SATISFIED
P3 = NOT_APPLICABLE
P4 = SATISFIED
```

P1 erzeugt `NO_REFERENCE`, weil ein Konflikt deklariert ist, aber kein
vollständiger Referenzrahmen mit Klasse und Scope vorliegt. Das Ergebnis
bestätigt weder, dass beide Anzeigen widersprüchlich sind, noch dass eine von
ihnen falsch ist.

## Robuste Handlung

Die ausgewählte Handlung `suspend-comparison-and-request-metadata` verändert
keinen Boots- oder Gerätezustand. Sie setzt lediglich die inhaltliche
Gleichsetzung der Labels aus und fordert an:

- Kanaldefinitionen,
- Messgröße und Achse,
- Nullpunkt und Einheit,
- Labelschwellen und Versuchsprotokoll.

Damit wird nicht „nichts entschieden“. Der Prozess entscheidet ausdrücklich,
dass eine Modellrevision ohne gemeinsamen Bezugspunkt noch nicht zulässig ist.

## Ausführung

Nach lokaler Installation:

```bash
rpf validate examples/wave-tank-no-reference-input-0.2.json
```

Der Befehl endet mit Exit-Code `0`, weil `NO_REFERENCE` ein gültiges
Prozessergebnis und kein technischer Eingabefehler ist.

## Grenzen

Das Beispiel zeigt nur den Umgang mit fehlenden Referenzmetadaten. Es bewertet
keine realen Instrumente, keine Fachperson und keine maritime Situation.
Insbesondere behauptet die Fixture nicht, dass Fachwissen nutzlos sei. Sie
trennt fachlich begründete Hypothesen von einer nachweislich dokumentierten
Zuordnung des konkreten Messkanals.
