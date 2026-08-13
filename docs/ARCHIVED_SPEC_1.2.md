# `ARCHIVED_SPEC_1.2`

## Die Referenzpunkt-Funktion (RPF) und das RPF-X-Reflexivitätsmodul

**Untertitel:** Ein hypothetisches Architekturmodell zur metakognitiven Selbstkalibrierung und Modellierung von Beobachter-Rückkopplungen unter Unsicherheit

| Feld | Wert |
| --- | --- |
| Version | RPF v1.2 |
| Archivkennung | `ARCHIVED_SPEC_1.2` |
| Status | `FROZEN DRAFT · IDLE` |
| Eingefroren | 23. Juli 2026 |
| Öffentliche Redaktion | 13. August 2026 |
| Validierung | empirisch und klinisch nicht validiert |

> **Archivhinweis:** Diese Datei ist die redaktionell normalisierte öffentliche
> Darstellung des am 23. Juli 2026 eingefrorenen Konzeptstands. Sie ist keine
> wortgetreue Transkription früherer Arbeitsgespräche. Rekonstruktionsgrenzen
> sind in [PROVENANCE.md](../PROVENANCE.md) offengelegt.

## 1. Geltungsbereich

Die RPF beschreibt eine abstrakte Prozessarchitektur für Situationen, in denen ein Ereignis mehr als eine plausible Interpretation zulässt, Informationen miteinander in Konflikt stehen oder die eigene Sicherheit nicht mit der externen Evidenz übereinstimmt.

Sie soll:

- automatische Interpretation zeitlich unterbrechen,
- die eigene Zuständigkeit und Kompetenz prüfen,
- den Referenzrahmen eines Konflikts bestimmen,
- interne Konfidenz und externe Evidenz getrennt halten,
- mehrere Hypothesen zulassen,
- Handlungsnutzen über mehr als den unmittelbaren Moment bewerten,
- und die Prüfung zuverlässig terminieren.

Die RPF behauptet weder objektive Wahrheit zu erzeugen noch Unsicherheit vollständig aufzulösen.

## 2. Basiskern RPF-0

Der bestätigte Basiskern lautet:

```text
[Ereignis E] → [Stopp] → [Selbstkalibrierung] → [Interpretation] → [Handlung]
```

Der Stopp isoliert das Ereignis zunächst von der ersten automatischen Deutung. Selbstkalibrierung bedeutet dabei nicht, eine gewünschte Deutung zu erzwingen, sondern die Bedingungen der eigenen Bewertung sichtbar zu machen.

## 3. RPF-3

Als bedienbare Kurzform lässt sich RPF-3 lesen als:

1. **Stopp** — Ereignis und automatische Interpretation vorläufig trennen.
2. **Kalibrieren** — Kompetenz, Referenzrahmen, interne Konfidenz und externe Evidenz prüfen.
3. **Interpretieren** — Hypothesen gewichten, zeitliche Folgen berücksichtigen und erst danach handeln.

Gegenüber RPF-0 umfasst RPF-3 vier ausdrücklich dokumentierte Architekturergänzungen:

- Kompetenzprüfung,
- duale Kalibrierung,
- Terminierungsschleife,
- temporale Adaptivität.

## 4. Prozessarchitektur

Der bestätigte Ablauf lautet:

```text
Ereignis
  → Referenzpunkt / Isolation
  → Kompetenzprüfung
  → epistemische Kalibrierung
  → Interpretation
  → adaptive Kalibrierung
  → Handlung
  → IDLE
```

Die kanonischen Zustandsbezeichnungen sind:

| Funktion | Zustandsbezeichnung |
| --- | --- |
| Transit / Bereitschaft | `IDLE` |
| Stopp / Trennung | `ISOLATION` |
| epistemische Operatoranwendung | `OPERATOR_APPL` |
| Prüfung des Informationszuwachses | `DELTA_EVAL` |
| Hypothesenerzeugung | `HYPOTHESIS_GEN` |
| adaptive und temporale Bewertung | `ADAPTIVE_VAL` |
| Handlung / Ausgabe | `OUTPUT_INTERFACE` |
| Kompetenzgrenze | `DELEGIERT` |
| fehlender Referenzpunkt | `NO_REFERENCE` |

Die vollständige Darstellung steht in [STATE_MACHINE.md](STATE_MACHINE.md).

## 5. Kompetenzaxiom

Vor der epistemischen Kalibrierung muss geprüft werden, ob System, Person oder Verfahren für den betreffenden Problemraum ausreichend kompetent ist.

Ist die Passung unzureichend, wird nicht durch zusätzliche Selbstsicherheit kompensiert. Der Prozess wechselt nach `DELEGIERT`: externe Expertise, bessere Evidenz oder ein geeigneteres Verfahren wird benötigt.

Eine Delegation ist ein gültiger Abschluss und kein Systemfehler.

## 6. Referenzrahmenklassifikation

Die RPF fragt vor einer globalen Wissensrevision:

> **„Auf welcher Ebene entsteht der scheinbare Widerspruch?“**

Mögliche Klassen sind:

- objektive Messung,
- subjektive Wahrnehmung,
- individuelle Präferenz,
- statistische Ausnahme,
- kulturelle Bewertung,
- sprachliche Mehrdeutigkeit,
- tatsächlicher logischer Widerspruch.

Kann kein belastbarer Referenzpunkt bestimmt werden, wird `NO_REFERENCE` ausgegeben. Unsicherheit wird dabei erhalten und nicht durch eine erfundene Referenz ersetzt.

## 7. Duale Kalibrierung

Die duale Kalibrierung hält zwei Größen ausdrücklich getrennt:

- `C_i` — interne Konfidenz: Wie sicher erscheint die eigene Interpretation?
- `C_e` — externe Evidenz: Wie stark wird die Interpretation durch überprüfbare externe Informationen getragen?

RPF v1.2 legt keine universelle Formel fest, die beide Größen zu einem einzigen Wahrheitswert verrechnet. Gerade eine Abweichung zwischen `C_i` und `C_e` ist relevante Information.

Beispiele für den Umgang mit einer Abweichung:

- hohes `C_i`, niedriges `C_e`: Sicherheit nicht mit Belegstärke verwechseln;
- niedriges `C_i`, hohes `C_e`: Evidenz prüfen und Unsicherheit gezielt aktualisieren;
- niedriges `C_i`, niedriges `C_e`: Urteil aussetzen oder weitere Information einholen;
- hohes `C_i`, hohes `C_e`: trotzdem Kompetenz- und Referenzrahmenprüfung beibehalten.

## 8. Interpretation und Hypothesenerzeugung

`HYPOTHESIS_GEN` erzeugt mehr als eine grundsätzlich prüfbare Einordnung, sofern die Informationslage dies zulässt. Eine Hypothese muss als Hypothese erkennbar bleiben.

Die Architektur unterscheidet mindestens:

- beobachtete Information,
- zugeschriebene Bedeutung,
- Konfidenz,
- Gegenhypothesen,
- verbleibende Unsicherheit.

Erst die Klassifikation eines Konflikts entscheidet, ob das bestehende Wissensmodell angepasst werden muss. Eine Perspektivdifferenz oder Präferenzabweichung erzwingt keine globale Modellrevision.

## 9. Adaptive und temporale Kalibrierung

`ADAPTIVE_VAL` bewertet nicht ausschließlich, welche Interpretation oder Handlung unmittelbar beruhigt, stabilisiert oder plausibel erscheint. Berücksichtigt werden auch mittlere und längere Zeithorizonte.

Die Prüfung fragt beispielsweise:

- Ist eine Handlung nur kurzfristig entlastend?
- Erzeugt sie später neue Abhängigkeit, Verzerrung oder Kosten?
- Bleibt sie bei fortbestehender Unsicherheit verhältnismäßig?
- Ist eine robuste, reversible Handlung verfügbar?

Temporale Adaptivität verhindert damit, unmittelbare Stabilität automatisch mit langfristigem Nutzen gleichzusetzen.

## 10. Terminierungsaxiom

Die RPF darf nicht zu unbegrenzter Prüfung oder rekursiver Selbstbeobachtung führen. Die bestätigten Abbruchkriterien werden in der öffentlichen Notation zusammengeführt als:

```text
Stop(RPF) ⇔ (ΔK ≤ ε) ∨ (n ≥ n_max) ∨ (T ≥ T_max) ∨ (B ≤ B_min)
```

Dabei bezeichnet:

- `ΔK` den marginalen Informations- oder Erkenntniszuwachs gegenüber der vorherigen Iteration,
- `ε` die kleinste als relevant definierte Zuwachsschwelle,
- `n` die Zahl der Iterationen,
- `n_max` die maximale Iterationszahl,
- `T` die bereits eingesetzte Zeit,
- `T_max` das Zeitlimit,
- `B` das verbleibende Ressourcenbudget,
- `B_min` das minimale Restbudget, bei dessen Erreichen beendet wird.

Ein Abbruch darf als Ergebnis „Unsicherheit bleibt bestehen“ liefern.

## 11. Ausgabevertrag

`OUTPUT_INTERFACE` soll mindestens kenntlich machen:

1. welche Information als Beobachtung behandelt wurde,
2. welcher Referenzrahmen angenommen wurde,
3. welche Interpretationen geprüft wurden,
4. wie `C_i` und `C_e` eingeschätzt wurden,
5. welche Unsicherheit verbleibt,
6. ob gehandelt, delegiert, ausgesetzt oder beendet wurde.

## 12. Invarianten

Innerhalb von RPF v1.2 gelten folgende Invarianten:

1. Interpretation wird nicht als Beobachtung ausgegeben.
2. Interne Sicherheit wird nicht als externe Evidenz ausgegeben.
3. Fehlende Kompetenz wird nicht durch zusätzliche Iterationen verdeckt.
4. Ein scheinbarer Widerspruch führt nicht vor seiner Referenzrahmenklassifikation zur globalen Wissensrevision.
5. Unsicherheit darf ein legitimes Endergebnis sein.
6. Jede Schleife besitzt ein Abbruchkriterium.
7. Archivierte Kennungen werden nicht für veränderte Fassungen wiederverwendet.

## 13. Nicht-Ziele

RPF v1.2 ist nicht:

- eine klinische Theorie,
- ein diagnostisches oder therapeutisches Protokoll,
- ein Beweis für die Richtigkeit einer Interpretation,
- ein Ersatz für Domänenexpertise,
- eine Aufforderung zu dauernder Selbstüberwachung,
- ein empirisch bestätigtes KI- oder Kognitionsmodell.

## 14. Änderungsregel

`ARCHIVED_SPEC_1.2` bleibt eingefroren. Korrekturen, Erweiterungen oder empirisch begründete Änderungen werden ausschließlich in einer neuen Versionslinie dokumentiert. Redaktionelle Hinweise dürfen das Archiv erläutern, aber nicht stillschweigend umschreiben.
