# Änderungsprotokoll

Alle nennenswerten Änderungen an der öffentlichen Dokumentation werden hier erfasst.

## Unreleased

- Ein Versions-Tag für die archivierten Fassungen steht noch aus.
- Nicht-normative Transferfallstudie zum OpenAI-/Hugging-Face-Sicherheitsvorfall
  ergänzt; dokumentierter Befund, RPF-Deutung und offene Hypothesen werden
  ausdrücklich getrennt.
- Eigenständig lesbare englische Projektübersicht ergänzt und von der deutschen
  README aus verlinkt.
- Englische Such- und Klassifikationsbegriffe in der Projektübersicht und den
  maschinenlesbaren Zitationsmetadaten ergänzt.
- Zweisprachige Entwicklungsroadmap mit der nächsten Zielstellung einer
  experimentellen Python-Implementierung und eines deterministischen
  Axiom-Validators ergänzt.
- Zweisprachige Designregel zur Trennung von Fähigkeit und Kalibrierung ergänzt
  und als Anforderung an Datenmodell, Statuslogik und Tests des Validators
  eingeplant.
- Zweisprachige Operationalisierung für A1–A4 und P1–P4 mit Eingabemodell,
  zweistufiger Statuslogik, stabilen Reason-Codes, Prioritätsregel und
  Mindesttestmatrix ergänzt.
- Experimentelles Python-Paket mit unveränderlichem typisiertem Datenmodell,
  stabilen Enums, Schemafehlern, JSON-Serialisierung und automatisierten Tests
  angelegt; Code separat unter `Apache-2.0` lizenziert.
- Experimentellen deterministischen Evaluator `0.2.0.dev0` für A1–A4 und
  P1–P4 ergänzt; Kompetenz-Gate, Statuspriorität, vollständige Regelspuren,
  Handlungsauswahl, 0.2-Schemata und neutraler Wetter-End-to-End-Test sind
  zweisprachig dokumentiert und durch 37 Tests abgedeckt.
- Öffentliche Schnittstelle `0.3.0.dev0` mit strengem versioniertem JSON-Parser,
  gebündeltem JSON-Schema, ausführbarer Wetter-Fixture sowie den Kommandos
  `rpf validate` und `rpf schema` ergänzt; Parser-, Schema-, CLI- und
  Kompatibilitätsverhalten ist zweisprachig dokumentiert und durch 58 Tests
  abgedeckt.
- Nicht-klinischen Loop-Collapse-Transferfall in eine schema-gültige
  Selbstbewertungs-Fixture (`DELEGATE`) und eine getrennte externe
  Mechanik-Fixture (`STOP`) aufgeteilt; Gate-, Divergenz-, Terminierungs-,
  Reflexivitäts- und Reversibilitätsspuren sind zweisprachig dokumentiert und
  durch insgesamt 60 Tests abgesichert.
- Nicht-klinische Koinzidenz-Interpretation als schema-gültige `WARN`-Fixture
  ergänzt; persönliche Auffälligkeit, Konfidenz, Evidenz und Kausalität bleiben
  getrennt, P1 meldet `REFERENCE_FRAME_AMBIGUOUS`, und die öffentliche
  Szenariomatrix ist zweisprachig dokumentiert. Der generische `WARN`-Hinweis
  benennt nun regelübergreifend alle Signale und Restunsicherheit; insgesamt 61
  Tests sichern den Stand ab.
- Zweisprachigen Transferfall zur Kontext-Rückkopplung und rückgespiegelten
  Begehrlichkeit ergänzt. Die neue neutrale `WARN`-Fixture trennt äußeren Reiz,
  wahrgenommene Norm, Defizit-Zuschreibung und eigenen Wunsch; ein bewusst
  niedrig gewichtetes und ein sozial folgenreicheres Beispiel markieren die
  gleiche Inferenzform ohne inhaltliche Gleichsetzung. Ein dokumentierter
  Kontext-Vervollständigungsfall (`Wort fehlt` → `not self`) ergänzt die
  Quellenprüfung. Insgesamt 62 Tests sichern den Stand ab.
- Zweisprachigen Transferfall zu Quellen-Echo und Referenzrahmen-Drift ergänzt.
  Er behandelt Quellenunabhängigkeit relativ zu einer atomaren Behauptung und
  Evidenzdimension, trennt gemeinsame Evidenzwurzel, semantische Drift und
  Scheinkonsens und markiert Claim-Provenienz als spätere Vertragserweiterung.
  Die neue schema-gültige Fixture erzeugt ausschließlich das deklarierte
  P1-`WARN`; insgesamt 63 Tests sichern den Stand ab.
- Zweisprachigen Wellenbecken-Transferfall als vollständige öffentliche
  `NO_REFERENCE`-Fixture ergänzt. Das synthetische Modellboot hält nur seine
  horizontale Station; die Anzeigen `HIGH` und `LOW` bleiben ohne Messgröße,
  Achse, Nullpunkt, Einheit und Labelsemantik unvergleichbar. Der Fall trennt
  Fachhypothesen von dokumentierten Kanaldefinitionen, schließt die öffentliche
  Statusmatrix und erhöht den Prüfstand auf 64 Tests.
- Experimentelle Runtime `0.4.0.dev0` für den RPF-Zustandsautomaten ergänzt.
  Kanonische Zustände und Ereignisse, eine unveränderliche deklarative
  Übergangstabelle, deterministische Übergangsfehler, eine feste Grenze von
  sieben Schritten sowie explizite `DELEGATE`-, `NO_REFERENCE`- und frühe oder
  adaptive `STOP`-Pfade erzeugen den versionierten Audit-Trace
  `rpf-state-machine-trace-0.1`. `rpf trace` macht ihn öffentlich ausführbar;
  Eingabe- und Validator-Ergebnisverträge bleiben unverändert auf 0.2. Die
  zweisprachige Dokumentation grenzt Kontrollfluss, Semantikanalyse und
  Wahrheitsprüfung ausdrücklich voneinander ab; insgesamt 80 Tests sichern den
  Stand ab.

## 2026-08-13 — Öffentlicher Repository-Entwurf

### Hinzugefügt

- eigenständig lesbare Repository-Struktur,
- archivierte Dokumentation für RPF v1.2 und RPF-X/IR v0.2,
- Zustandsautomat, Axiome, Referenzrahmenklassifikation und Glossar,
- Lizenz `CC BY-NC-SA 4.0`,
- Zitierdatei und Nutzungshinweise,
- redaktionelle Provenienz und Rekonstruktionsgrenzen.

### Redaktionell entschieden

- Persönliche Entstehungssituationen werden nicht veröffentlicht.
- Ein neutraler Prognosekonflikt dient als einziges Anwendungsbeispiel.
- Unvollständig überlieferte Formeln werden nicht rekonstruiert.

### Konzeptänderungen

- Keine. Der eingefrorene Architekturstand bleibt `ARCHIVED_SPEC_1.2` beziehungsweise `ARCHIVED_RPF-X_IR_0.2`.

## 2026-07-23 — Archivierung

- RPF v1.2 als `ARCHIVED_SPEC_1.2` eingefroren.
- RPF-X/IR v0.2 als `ARCHIVED_RPF-X_IR_0.2` eingefroren.
- Lebenszyklusstatus auf `FROZEN DRAFT · IDLE` gesetzt.
