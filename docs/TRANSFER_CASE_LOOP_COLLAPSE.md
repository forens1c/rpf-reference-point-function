# Nicht-klinischer Transferfall: Loop Collapse

**Sprachen:** Deutsch · [English](TRANSFER_CASE_LOOP_COLLAPSE.en.md)

## Status und Zweck

Dieser Transferfall untersucht eine **synthetische** kognitive Schleife als
Negativfall für den experimentellen Validator. Er ist nicht normativ, nicht
empirisch validiert und keine Erweiterung der eingefrorenen RPF-Spezifikationen.

Die Analogie wurde durch ein Szenario angeregt, in dem ein beeinträchtigter
Entscheidungsprozess ein internes Alarmsignal mit einer äußeren Bedrohung
verwechselt und eine weitere Zustandsänderung erwägt. Die ausführbaren
Fixtures formulieren dies absichtlich abstrakt und nicht klinisch.

Sie stellen insbesondere nicht fest:

- ob eine reale Umgebung sicher oder gefährlich ist,
- wodurch ein reales körperliches oder psychisches Signal verursacht wird,
- ob eine Person kompetent, berauscht oder erkrankt ist,
- welche medizinische, psychologische oder praktische Maßnahme richtig ist.

## Warum zwei Fixtures erforderlich sind

A1 ist im aktuellen Validator ein echtes Kompetenz-Gate. Eine unzureichende
Kompetenz führt zu `DELEGATE`; die nachfolgenden Regeln werden dann bewusst als
`NOT_EVALUATED` protokolliert. Ein einzelner Lauf kann deshalb nicht zugleich
eine unzureichende A1-Kompetenz und ausgewertete A2-/A3-Verstöße behaupten.

Der Fall wird daher in zwei klar getrennte Bewertungs-Fixtures aufgeteilt:

| Fixture | Bewerteter Prozess | Erwartetes Ergebnis |
| --- | --- | --- |
| [Selbstbewertung](../examples/loop-collapse-self-input-0.2.json) | Das synthetische Subjekt bewertet seinen eigenen, ausdrücklich beeinträchtigten Prozess. | `DELEGATE` |
| [Extern dokumentierter Mechanikfall](../examples/loop-collapse-external-input-0.2.json) | Ein externer Testautor liefert einen Prozessdatensatz, in dem die aufgabenspezifische Kompetenz des bewerteten Prozesses als ausreichend deklariert ist. | `STOP` |

Die Rollenunterscheidung steht derzeit in `problem_domain`, Begründung und
Provenienz. Der Eingabevertrag besitzt noch keine eigenen Felder für
Bewertungssubjekt und Bewertungsinstanz.

## Selbstbewertung und A1-Gate

Die Selbstbewertungs-Fixture deklariert `competence.status` als
`INSUFFICIENT`. Der Validator erzeugt deshalb:

```text
overall_status = DELEGATE
A1 = TRIGGERED · COMPETENCE_INSUFFICIENT
A2–A4, P1–P4 = NOT_EVALUATED
```

Die auffälligen Kalibrierungs- und Terminierungswerte bleiben zwar als Eingabe
erhalten, werden aber nicht fachlich bewertet. Genau dies ist die beabsichtigte
Schutzwirkung des Kompetenz-Gates.

## Extern dokumentierter Mechanikfall und erhaltene Signale

Die zweite Fixture ersetzt die Kompetenz des bewerteten Prozesses nicht durch
die Kompetenz eines Beobachters. Sie setzt für einen eigenständigen
Mechaniktest voraus, dass der bewertete Prozess aufgabenspezifisch kompetent
ist, aber aktuell eine starke Kalibrierungsdivergenz und überschrittene Grenzen
aufweist. Der externe Testautor liefert lediglich Datensatz und Provenienz.

Diese Testvoraussetzung übernimmt keine medizinische oder faktische Autorität.
Mit vergleichbar deklarierten Werten `C_i = 0.98`, `C_e = 0.02` und einer
experimentellen Divergenzschwelle von `0.4` ergibt sich:

```text
overall_status = STOP
A1 = SATISFIED
A2 = SIGNAL    · CONFIDENCE_EVIDENCE_DIVERGENCE
A3 = TRIGGERED · INFORMATION_GAIN_LIMIT
               · ITERATION_LIMIT
               · TIME_LIMIT
               · RESOURCE_LIMIT
A4 = SATISFIED
P1 = SATISFIED
P2 = SATISFIED
P3 = TRIGGERED · REFLEXIVE_DEPTH_LIMIT
P4 = SIGNAL    · IRREVERSIBLE_ACTION_UNJUSTIFIED
```

Der Gesamtstatus `STOP` verdrängt die niedrigeren Signale nicht. Die
vollständige Regelspur zeigt weiterhin, dass Kalibrierungsdivergenz,
Terminierungsgrenzen und eine unbegründete irreversible Auswahl gleichzeitig
im bereitgestellten Prozess vorkommen.

Die Fixture ist damit eine Mechanikdemonstration und keine Behauptung, dass eine
konkrete beeinträchtigte Person tatsächlich kompetent sei. Der aktuelle Vertrag
kann die Rollen und Herkunft jeder einzelnen Angabe noch nicht formal erzwingen.

## Übersetzung in den bestehenden 0.2-Vertrag

| Ausgangsidee | Ausführbare Darstellung |
| --- | --- |
| numerische Kompetenz `0.15` | Enum `INSUFFICIENT`; der Validator besitzt keine kanonische Kompetenzschwelle |
| `SUBJECTIVE_EMOTIONAL` | bestehende Klassen `SUBJECTIVE_PERCEPTION` und `OBJECTIVE_MEASUREMENT` |
| Restunsicherheit `0.85` | strukturierte Unsicherheitsobjekte ohne erfundenen Gesamtscore |
| Schleifentiefe `412 > 50` | A3 `iteration/max_iterations` und P3 `recursion_depth/max_recursion_depth` |
| `robustness_score` | nicht implementiert; P4 prüft Auswahl, Reversibilität, Begründung und deklarierte Constraints |
| `NON_ROBUST_ACTION_SELECTION` | vorhandener Code `IRREVERSIBLE_ACTION_UNJUSTIFIED` für die konkrete Fixture |

Die alternative Handlung `pause-and-delegate` ist eine abstrakte
Prozessoption. Sie ist keine Atem-, Vagus-, Sucht- oder Therapieempfehlung.

## Ausführung

Nach lokaler Installation:

```bash
rpf validate examples/loop-collapse-self-input-0.2.json
rpf validate examples/loop-collapse-external-input-0.2.json
```

Beide Befehle enden technisch mit Exit-Code `0`, weil `DELEGATE` und `STOP`
gültige Validator-Ergebnisse und keine Eingabefehler sind.

## Offene Architekturfrage

Der Fall macht eine echte Modellfrage sichtbar: Ein künftiger Vertrag könnte
Bewertungssubjekt, Bewertungsinstanz und Herkunft ihrer jeweiligen Angaben
explizit trennen. Vor einer solchen Schemaänderung muss geklärt werden:

1. Wessen Kompetenz wird beurteilt?
2. Wer liefert `C_i`, `C_e`, Beobachtung und Provenienz?
3. Wann ist eine externe Quelle wirklich unabhängig?
4. Wie bleibt verhindert, dass getrennte Dimensionen zu einem scheinbar
   objektiven Personen- oder Risikoscore verschmolzen werden?

Diese Frage wird als mögliche spätere Schemaentwicklung dokumentiert. Die
vorliegenden Fixtures ändern weder den 0.2-Datenvertrag noch die
Evaluatorregeln.
