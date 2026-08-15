# RPF-Entwicklungsroadmap

**Sprachen:** Deutsch · [English](ROADMAP.en.md)

## Status dieser Roadmap

Diese Roadmap beschreibt mögliche nächste Entwicklungsschritte. Sie ist
**nicht-normativ**, enthält keine zeitlichen Zusagen und verändert weder
`ARCHIVED_SPEC_1.2` noch `ARCHIVED_RPF-X_IR_0.2`.

Experimentelle Implementierungsentscheidungen, Schwellenwerte und Datenmodelle
gehören nicht automatisch zum eingefrorenen RPF-Kern. Abweichungen und spätere
Änderungen müssen nachvollziehbar dokumentiert werden.

## Nächste Zielstellung

Die **experimentelle Python-Referenzimplementierung** besitzt inzwischen einen
deterministischen Axiom-Validator, eine öffentliche JSON-/CLI-Schnittstelle,
einen ausführbaren Zustandsautomaten und den getrennten, nicht-autorisierenden
Vorschlagsvertrag `rpf-classification-proposal-0.1`.

Als nächster abgegrenzter Schritt ist ein kleiner deterministischer,
regelbasierter Klassifikationsanbieter vorgesehen. Er soll ausschließlich den
neuen Vorschlagsvertrag erzeugen. Ein Adapter zum `ValidatorInput`, eine
automatische Semantikanalyse und ein Sprachmodell bleiben spätere, getrennt
versionierte Schritte.

Der Validator soll nicht entscheiden, ob eine Aussage wahr ist. Er soll prüfen,
ob ein Kalibrierungs- und Entscheidungsprozess:

- die eigene Kompetenzpassung berücksichtigt,
- interne Konfidenz und externe Evidenz getrennt hält,
- den Referenzrahmen vor einer globalen Revision bestimmt,
- verbleibende Unsicherheit ausdrücklich ausgibt,
- Terminierungs- und Ressourcengrenzen einhält,
- Handlungsfolgen über mehrere Zeithorizonte betrachtet.

Vorgesehene strukturierte Ergebniszustände sind beispielsweise `PASS`, `WARN`,
`DELEGATE`, `NO_REFERENCE` und `STOP`. Das Auslösen einer Schutzregel ist dabei
nicht automatisch eine Axiomverletzung: Eine Delegation bei unzureichender
Kompetenz oder eine regelgerechte Terminierung wären beabsichtigte
RPF-Ergebnisse.

Ein zusätzliches experimentelles Implementierungsprinzip ist die
[Trennung von Fähigkeit und Kalibrierung](docs/CAPABILITY_CALIBRATION_SEPARATION.md):
Kompetenzpassung, interne Konfidenz, externe Evidenz, Referenzrahmenpassung und
zeitliche Adaptivität werden getrennt geprüft. Hohe Fähigkeit allein darf
keinen `PASS`-Status erzeugen.

Die erste [Operationalisierungstabelle für A1–A4 und P1–P4](docs/VALIDATOR_OPERATIONALIZATION.md)
legt dafür Eingabefelder, Regelergebnisse, Prozessstatus, Reason-Codes und
Mindesttests fest. Sie ist das vorläufige Arbeitsdokument für Datenmodell und
Validator, keine Änderung des eingefrorenen Kerns.

## Entwicklungsgrundsätze

1. **Deterministischer Kern zuerst:** Die grundlegenden Regeln sollen ohne ein
   Sprachmodell ausführbar und testbar sein.
2. **Prozess statt Wahrheitsversprechen:** Geprüft wird die Qualität und
   Nachvollziehbarkeit des Verfahrens, nicht die objektive Wahrheit einer
   Schlussfolgerung.
3. **Explizite Datenherkunft:** Eingaben, Schwellenwerte, ausgelöste Regeln und
   Restunsicherheit sollen in der Ausgabe erkennbar bleiben.
4. **Experimentelle Schwellenwerte:** Zahlenwerte dürfen nicht ohne Begründung
   als kanonischer Teil der RPF ausgegeben werden.
5. **Trennung der Ebenen:** Validator, Zustandsautomat,
   Referenzrahmenklassifikation und optionale KI-Komponenten bleiben getrennte
   Module.
6. **Keine stillschweigende Revision:** Die archivierten Spezifikationen werden
   durch den Code weder überschrieben noch rückwirkend umgedeutet.
7. **Fähigkeit ist keine Kalibrierung:** Kompetenz, Konfidenz, Evidenz,
   Referenzrahmenpassung und zeitliche Adaptivität bleiben getrennte
   Prüfdimensionen mit eigener Begründung und Datenherkunft.

## Geplante Etappen

### 0 — Technische Operationalisierung

- Für jedes Axiom erforderliche Eingaben, Prüfregeln und Ausgaben definieren.
- Klären, welche Größen direkt messbar sind und welche eine deklarierte oder
  externe Beurteilung benötigen.
- Bedeutung und Skalen von Kompetenzpassung, `C_i`, `C_e`, `ΔK`, Zeit und
  Ressourcen präzisieren.
- Referenzrahmenpassung und zeitliche Adaptivität als von Kompetenz und
  Konfidenz unabhängige Prüfdimensionen operationalisieren.
- Experimentelle Schwellenwerte ausdrücklich als Konfiguration kennzeichnen.

### 1 — Datenmodell und Ergebnisschema

- Typisierte Eingaben für Problemkontext, Kompetenzpassung, Konfidenz, Evidenz,
  Referenzrahmen und Ressourcen festlegen.
- Verhindern, dass getrennte Prüfdimensionen stillschweigend zu einem einzigen
  Vertrauenswert zusammengeführt werden.
- Strukturierte Ergebnisse mit Status, Begründung, ausgelösten Regeln und
  Restunsicherheit definieren.
- Wertebereiche und fehlende Pflichtangaben validieren.

### 2 — Deterministischer Axiom-Validator

- Kompetenzprüfung mit dem Ergebnis `DELEGATE` umsetzen.
- Sicherstellen, dass hohe Kompetenz oder Konfidenz allein niemals `PASS`
  auslöst.
- Trennung von `C_i` und `C_e` prüfen; auffällige Abweichungen zunächst als
  Kalibrierungssignal statt als automatischen Fehler behandeln.
- Terminierung nach Informationsgewinn, Iterationen, Zeit und Ressourcen
  implementieren.
- Prüfung mehrerer Zeithorizonte und reversibler Handlungsoptionen abbilden.
- Maschinenlesbare und für Menschen verständliche Begründungen ausgeben.

### 3 — Tests und neutraler Referenzfall

- Unit-Tests für jeden Regel- und Ergebniszustand anlegen.
- Grenzwerte, ungültige Eingaben und fehlende Referenzpunkte testen.
- Das neutrale Wetterbeispiel als ersten vollständigen End-to-End-Fall
  implementieren.
- Sicherstellen, dass gleiche Eingaben reproduzierbare Ergebnisse erzeugen.

### 4 — RPF-Zustandsautomat

- [x] Den bestehenden Zustandsraum als ausführbare Übergangslogik modellieren.
- [x] Zulässige und unzulässige Übergänge testen.
- [x] Delegation, `NO_REFERENCE`, Terminierung und Rückkehr zu `IDLE`
  protokollieren.

### 5 — Optionale Klassifikation und KI-Experimente

- [x] Einen versionierten, nicht-autorisierenden Vertrag für
  Klassifikationsvorschläge definieren.
- [x] Status, Klassen, Provider-Konfidenz, Unsicherheit und belegende
  Textfragmente als getrennte Dimensionen modellieren.
- [x] Verhindern, dass ein Vorschlag Prozessstatus, Reason-Codes,
  Zustandsübergänge, Kompetenz, Evidenzwerte oder Handlungen festlegt.
- [x] Neutrale Positiv- und Negativ-Fixtures für die Vertragsgrenze
  veröffentlichen.
- Eine regelbasierte Referenzrahmenklassifikation vor einer KI-Variante prüfen.
- KI-Ausgaben nur als Hypothesen behandeln und durch denselben Validator führen.
- Prüfen, ob ein späteres Schema Bewertungssubjekt, Bewertungsinstanz und die
  Herkunft ihrer jeweiligen Angaben ausdrücklich trennen muss.
- Quellenunabhängigkeit behauptungsbezogen und nach Daten-, Analyse-, Methoden-,
  Kontext- und Provenienzdimension modellieren.
- Für einen späteren, versionierten Claim-Vertrag Evidenzwurzeln,
  Ableitungskanten, Geltungsbereich, epistemische Modalität und Kausalstatus
  untersuchen.
- Den KI-Agenten-Transferfall als anspruchsvollen Untersuchungsfall nutzen, ohne
  daraus eine Validierung der RPF abzuleiten.
- Autorisierung und technische Erreichbarkeit in sicherheitsbezogenen Versuchen
  ausdrücklich getrennt halten.

### 6 — Experimentelle Evaluation

- Testkriterien und Vergleichsbedingungen vor Experimenten dokumentieren.
- Fehlalarme, übersehene Konflikte, Terminierungsverhalten und Erklärbarkeit
  untersuchen.
- Ergebnisse getrennt von der eingefrorenen Spezifikation veröffentlichen.

## Erster geplanter Meilenstein

- [x] [Operationalisierungstabelle für A1–A4 und P1–P4](docs/VALIDATOR_OPERATIONALIZATION.md) erstellen
- [x] Trennung von Fähigkeit und Kalibrierung in Datenmodell und Tests abbilden
- [x] separate Softwarelizenz für neuen Code festlegen (`Apache-2.0`)
- [x] minimales Python-Paket und typisiertes Ein-/Ausgabeschema anlegen
- [x] deterministischen Axiom-Validator implementieren
- [x] automatisierte Unit-Tests ergänzen
- [x] Wetterbeispiel als End-to-End-Test umsetzen
- [x] Grenzen und experimentelle Annahmen dokumentieren

Der erste Implementierungsmeilenstein ist damit in der experimentellen
[Validator-Implementierung 0.2](docs/VALIDATOR_IMPLEMENTATION_0.2.md) erreicht.

## Abgeschlossener technischer Schnitt 0.3

Version 0.3 macht die öffentliche Schnittstelle direkt nutzbar:

- [x] versionierten Parser für JSON-Eingaben entwickeln,
- [x] ein maschinenlesbares JSON-Schema veröffentlichen,
- [x] den neutralen Wetterfall als ausführbare Beispieldatei bereitstellen,
- [x] `rpf validate scenario.json` und `rpf schema` ergänzen,
- [x] Parser-, CLI- und Kompatibilitätstests hinzufügen.

Die Einzelheiten stehen in
[JSON-Schnittstelle und CLI 0.3](docs/JSON_CLI_0.3.md). Die Paketversion
`0.3.0.dev0` verwendet weiterhin die unveränderten Ein- und Ergebnisverträge
`rpf-validator-input-0.2` und `rpf-validator-result-0.2`.

## Abgeschlossener technischer Schnitt 0.4

Version 0.4 setzt Etappe 4 als ausführbaren, begrenzten Kontrollfluss um:

- [x] kanonische Zustände und Ereignisse als typsichere Enums abbilden,
- [x] zulässige Übergänge in einer unveränderlichen Tabelle veröffentlichen,
- [x] ungültige Übergänge deterministisch ablehnen,
- [x] `DELEGATE`, `NO_REFERENCE` und frühe beziehungsweise adaptive `STOP`-Pfade
  protokollieren,
- [x] jeden erfolgreichen Lauf innerhalb von höchstens sieben Übergängen zu
  `IDLE` zurückführen,
- [x] Validator und Runtime ausschließlich über
  `rpf-validator-result-0.2` koppeln,
- [x] den versionierten Audit-Trace `rpf-state-machine-trace-0.1` und
  `rpf trace scenario.json` ergänzen.

Die Einzelheiten stehen im
[ausführbaren Zustandsautomaten 0.4](docs/STATE_MACHINE_RUNTIME_0.4.md). Die
Paketversion `0.4.0.dev0` verwendet weiterhin die unveränderten Eingabe- und
Ergebnisverträge `rpf-validator-input-0.2` und
`rpf-validator-result-0.2`.

## Abgeschlossener technischer Schnitt 0.5

Version 0.5 schafft die erste maschinenlesbare Grenze für optionale
Klassifikationsanbieter, ohne ihnen Bewertungsautorität zu geben:

- [x] den Vorschlagsvertrag `rpf-classification-proposal-0.1` versionieren,
- [x] unveränderliche Python-Modelle, einen strikten Parser und ein
  Draft-2020-12-JSON-Schema bereitstellen,
- [x] Provider-Identität, Konfigurations-Digest, Quellbindung und
  byte-adressierte Evidenzfragmente protokollieren,
- [x] Frame-Status und Frame-Klassen sowie Provider-Konfidenz und `C_i`/`C_e`
  ausdrücklich trennen,
- [x] unbekannte Felder und autorisierende Eingriffe deterministisch ablehnen,
- [x] drei neutrale öffentliche Vorschläge und einen Negativfall-Katalog
  veröffentlichen,
- [x] Validator-Eingabe, Validator-Ergebnis und State-Machine-Trace unverändert
  lassen.

Die Einzelheiten stehen im
[Klassifikationsvorschlagsvertrag 0.1](docs/CLASSIFICATION_PROPOSAL_CONTRACT_0.1.md).
Die Paketversion `0.5.0.dev0` enthält absichtlich noch keinen Provider und
keinen Adapter.

## Nächster technischer Schnitt

Der nächste Schnitt setzt Etappe 5 mit einem kleinen regelbasierten Anbieter
fort, ohne bereits ein Sprachmodell oder einen Adapter in den Kern einzubauen:

- einen kleinen, deterministischen Provider hinter einer schmalen
  Python-Schnittstelle implementieren,
- den vertrauenswürdigen Aufrufkontext beziehungsweise eine Provider-Registry
  getrennt von der Provider-Ausgabe definieren,
- reproduzierbare Vorschläge für wenige ausdrücklich begrenzte Regeln erzeugen,
- Vertrags-, Provenienz- und Reproduzierbarkeitstests ergänzen,
- weiterhin testen, dass der Anbieter weder Validator noch Übergangstabelle
  aufruft oder Prozessstatus festlegt.

Erst nach diesem Provider-Schnitt soll ein Adapter mit expliziter Feld-Allowlist,
Bindungsprüfung und eigenem Mapping-Trace entworfen werden. Erst dieser Adapter
könnte einen Vorschlag zusammen mit einem unabhängig gelieferten Basisfall in
Richtung `ValidatorInput` übersetzen.

Eine automatische Semantikanalyse bleibt eine spätere austauschbare Variante.
Der deterministische Kern kann strukturwidrige oder unvollständige Vorschläge
abweisen, aber keine intern konsistent eingetragene Falschinformation ohne
zusätzliche Evidenz als unwahr erkennen.

Kompatibilitäts- und Migrationsregeln für spätere Vorab-Schemata bleiben
parallel als offene Aufgabe bestehen. Dazu gehört die im
[Loop-Collapse-Transferfall](docs/TRANSFER_CASE_LOOP_COLLAPSE.md) sichtbar
gewordene Rollenfrage zwischen Bewertungssubjekt und Bewertungsinstanz. Der
[Quellen-Echo-Transferfall](docs/TRANSFER_CASE_SOURCE_ECHO.md) ergänzt als
weitere parallele Aufgabe eine behauptungsbezogene Provenienzstruktur; sie
wird nicht stillschweigend in den bestehenden 0.2-Eingabevertrag aufgenommen.

## Nicht-Ziele des ersten Prototyps

Der erste Prototyp ist ausdrücklich:

- kein Wahrheitsdetektor,
- kein autonomes Autorisierungssystem,
- kein medizinisches, psychologisches oder diagnostisches Werkzeug,
- keine empirische Bestätigung der RPF,
- keine validierte KI-Sicherheitsarchitektur,
- kein Ersatz für Fachkompetenz oder externe Evidenz.

## Mitwirkung und Änderungsnachweise

Vorschläge, Testfälle und Implementierungen können später über GitHub Issues und
Pull Requests eingebracht werden. Beiträge sollten deutlich trennen zwischen:

1. dokumentiertem RPF-Kern,
2. experimenteller Implementierungsentscheidung,
3. empirischem Befund,
4. Interpretation oder neuer Hypothese.

Konzeptänderungen benötigen eine eigene Versionskennung. Der
Implementierungscode steht gesondert unter `Apache-2.0`; die bestehende
Dokumentationslizenz `CC BY-NC-SA 4.0` gilt nicht für diesen Code.
