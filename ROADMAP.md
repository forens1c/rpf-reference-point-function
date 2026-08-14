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

Geplant ist eine **experimentelle Python-Referenzimplementierung**. Ihr erster
Meilenstein soll ein deterministischer Axiom-Validator sein.

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

- Den bestehenden Zustandsraum als ausführbare Übergangslogik modellieren.
- Zulässige und unzulässige Übergänge testen.
- Delegation, `NO_REFERENCE`, Terminierung und Rückkehr zu `IDLE` protokollieren.

### 5 — Optionale Klassifikation und KI-Experimente

- Eine regelbasierte Referenzrahmenklassifikation vor einer KI-Variante prüfen.
- KI-Ausgaben nur als Hypothesen behandeln und durch denselben Validator führen.
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
- [ ] Trennung von Fähigkeit und Kalibrierung in Datenmodell und Tests abbilden
- [ ] separate Softwarelizenz für neuen Code festlegen
- [ ] minimales Python-Paket und Ergebnisschema anlegen
- [ ] deterministischen Axiom-Validator implementieren
- [ ] automatisierte Unit-Tests ergänzen
- [ ] Wetterbeispiel als End-to-End-Test umsetzen
- [ ] Grenzen und experimentelle Annahmen dokumentieren

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

Konzeptänderungen benötigen eine eigene Versionskennung. Implementierungscode
soll eine gesonderte Softwarelizenz erhalten; die bestehende
Dokumentationslizenz `CC BY-NC-SA 4.0` gilt nicht automatisch für zukünftigen
Code.
