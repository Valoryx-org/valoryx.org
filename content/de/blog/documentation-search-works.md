---
title: "Wie Dokumentationssuche wirklich funktioniert"
description: "Die meisten Dokumentationstools verwenden einfachen Keyword-Abgleich oder erfordern Elasticsearch. DocPlatform bettet Bleve für Volltextsuche mit Stemming und Fuzzy-Matching ein — ohne zusätzliche Dienste."
date: "2026-04-02"
author: "Valoryx Team"
tags: ["search", "architecture", "documentation"]
---

Sie tippen eine Abfrage in die Suchleiste Ihrer Dokumentation. Ergebnisse erscheinen. Aber was passiert zwischen dem Tastendruck und den Ergebnissen? Bei den meisten Dokumentationsplattformen lautet die Antwort entweder „nicht viel" (einfacher Keyword-Abgleich, der offensichtliche Ergebnisse übersieht) oder „eine Menge Infrastruktur" (ein Elasticsearch-Cluster, den Ihr Ops-Team warten muss).

Es gibt einen Mittelweg, den die meisten Teams nicht kennen: eingebettete Volltextsuche. DocPlatform verwendet [Bleve](https://blevesearch.com/), eine in Go geschriebene Suchbibliothek, die direkt in das Binary kompiliert wird. Keine externen Dienste, keine Netzwerkaufrufe, kein Cluster zu verwalten — aber mit den Funktionen, die Sie tatsächlich brauchen: Stemming, Fuzzy-Matching, Field-Boosting und Relevanz-Ranking.

So funktioniert es von Grund auf.

## Warum Keyword-Abgleich versagt

Die einfachste Suchimplementierung ist `LIKE '%query%'` in SQL. Das bekommen Sie, wenn ein Entwickler Suche als Nachgedanke hinzufügt. Es funktioniert für exakte Treffer, versagt aber in jedem anderen Fall:

- Die Suche nach „installieren" findet keine Seiten mit „Installation" oder „installiert"
- Die Suche nach „Authn" findet keine Seiten über „Authentifizierung"
- Ein Tippfehler wie „Deploymnet" liefert nichts
- Jedes Ergebnis hat dasselbe Ranking — eine Seite mit dem Titel „Installationsanleitung" rangiert genauso wie eine Seite, die „installieren" einmal in der Fußzeile erwähnt

Manche Plattformen verbessern das mit der FTS5-Erweiterung von SQLite, die Tokenisierung und einfaches Ranking hinzufügt. Das ist ein Fortschritt, aber es fehlen weiterhin Stemming, Fuzzy-Matching und die Möglichkeit, bestimmte Felder (wie Titel) gegenüber anderen zu boosten.

## Was Volltextsuche wirklich macht

Eine richtige Suchmaschine verarbeitet Text in zwei Phasen: Indizierung (wenn Inhalt geschrieben wird) und Abfrage (wenn jemand sucht). Beide Phasen leisten mehr Arbeit, als Sie erwarten würden.

### Indizierung: Was passiert, wenn Sie eine Seite speichern

Wenn Sie eine Seite in DocPlatform erstellen oder aktualisieren, durchläuft der Inhalt eine Analyse-Pipeline, bevor er indiziert wird:

**1. Tokenisierung** — Der Text wird in einzelne Begriffe aufgeteilt. „Erste Schritte mit DocPlatform" wird zu `["erste", "schritte", "mit", "docplatform"]`.

**2. Kleinschreibung** — Alle Tokens werden auf Kleinschreibung normalisiert. „DocPlatform" und „docplatform" stimmen überein.

**3. Stoppwort-Entfernung** — Häufige Wörter wie „der", „ist", „mit", „ein" werden entfernt. Sie kommen in fast jedem Dokument vor und helfen nicht, relevante Ergebnisse zu unterscheiden.

**4. Stemming** — Wörter werden auf ihre Stammform reduziert. „installieren", „Installation" und „installiert" werden alle zu „install". Das bedeutet, eine Suche nach einem dieser Wörter findet alle.

**5. Feldtrennung** — Verschiedene Teile des Dokuments werden separat indiziert. Titel, Text, Tags und Pfad bekommen jeweils ein eigenes Feld im Index. Das ermöglicht Field-Boosting bei der Abfrage.

Der resultierende Index ist eine Datenstruktur namens invertierter Index — eine Zuordnung von jedem Begriff zur Liste der Dokumente, die ihn enthalten, zusammen mit Positionsinformationen (wo im Dokument der Begriff vorkommt und wie oft).

```
"install"    → [doc_3 (Titel, Pos:0), doc_7 (Text, Pos:45), doc_12 (Text, Pos:102)]
"deploy"     → [doc_3 (Text, Pos:23), doc_5 (Titel, Pos:0)]
"kubernetes" → [doc_5 (Text, Pos:15), doc_5 (Text, Pos:89)]
```

### Abfrage: Was passiert, wenn Sie suchen

Wenn ein Benutzer eine Abfrage eingibt, führt die Suchmaschine dieselbe Analyse-Pipeline auf dem Abfragetext aus (Tokenisieren, Kleinschreibung, Stemming), und sucht dann jeden Begriff im invertierten Index nach.

Aber der eigentliche Wert liegt im Ranking. Nicht alle Treffer sind gleich. Bleve verwendet eine TF-IDF-Variante (Term Frequency, Inverse Document Frequency) kombiniert mit Field-Boosting, um einen Relevanzwert zu erzeugen:

- **Termhäufigkeit:** Eine Seite, die „Deployment" 10 Mal erwähnt, ist wahrscheinlich relevanter als eine, die es einmal erwähnt.
- **Inverse Dokumenthäufigkeit:** Ein Begriff, der nur in 3 von 500 Dokumenten vorkommt, ist aussagekräftiger (und nützlicher für das Ranking) als ein Begriff, der in 400 Dokumenten vorkommt.
- **Field-Boost:** Ein Treffer im Titel ist mehr wert als ein Treffer im Text. In DocPlatform bekommen Titel-Treffer einen 3x-Boost, Tag-Treffer 2x und Text-Treffer 1x.

Die Formel erzeugt einen numerischen Score für jedes passende Dokument, und die Ergebnisse werden nach Score sortiert zurückgegeben.

## Fuzzy-Matching: Tippfehler verarbeiten

Echte Benutzer machen Tippfehler. „Kuberntes" statt „Kubernetes". „Authentcation" statt „Authentication". Einfache Suche liefert für diese Abfragen nichts.

Bleve unterstützt Fuzzy-Matching mittels Editierdistanz (Levenshtein-Distanz). Ein Abfragebegriff stimmt mit einem Dokumentbegriff überein, wenn sie sich um N oder weniger Zeichenoperationen unterscheiden (Einfügungen, Löschungen, Ersetzungen). DocPlatform verwendet standardmäßig eine Editierdistanz von 1 — ausreichend, um einzelne Tippfehler zu erkennen, ohne zu viele falsch positive Ergebnisse zu erzeugen.

```
Abfrage: "authentcation"
Editierdistanz 1: stimmt mit "authentication" überein (ein fehlendes 'i')
Ergebnisse: alle Dokumente mit "authentication"
```

Das geschieht transparent. Benutzer müssen nichts über Fuzzy-Matching wissen oder konfigurieren. Sie suchen einfach und erhalten Ergebnisse, selbst wenn sie sich vertippen.

## Wie DocPlatform den Index synchron hält

Der schwierige Teil eingebetteter Suche ist nicht die Suche selbst — es ist, den Index konsistent mit dem Inhalt zu halten. DocPlatform hat zwei Inhaltsquellen: den Web-Editor und Git. Beide können Seiten erstellen, aktualisieren und löschen.

Hier ist der Indizierungsablauf:

**Web-Editor-Speicherung:** Benutzer klickt Speichern → Inhalt wird in die Datenbank geschrieben → der Suchindexer aktualisiert den Bleve-Index → die Git-Sync-Engine committed die Änderung.

**Git-Push empfangen:** Git-Webhook feuert → die Sync-Engine pullt Änderungen → neue/geänderte Seiten werden in die Datenbank geschrieben → der Suchindexer aktualisiert den Bleve-Index.

**Massenoperationen:** Wenn Sie ein Repository mit Hunderten von Markdown-Dateien importieren, verarbeitet der Indexer sie in Batches. Ein 500-Seiten-Import dauert auf bescheidener Hardware etwa 3 Sekunden für die vollständige Indizierung.

**Löschungen:** Wenn eine Seite gelöscht wird (über die Web-Oberfläche oder Git), wird das entsprechende Dokument aus dem Bleve-Index entfernt. Keine verwaisten Suchergebnisse.

Das wichtige Detail: Die Indizierung ist synchron mit dem Schreibvorgang. Wenn das Speichern/der Sync abgeschlossen ist, ist der Suchindex bereits aktualisiert. Es gibt keine „Warten auf Neuindizierung"-Verzögerung. Das ist möglich, weil Bleve im selben Prozess läuft — es gibt keinen Netzwerk-Hop zu einem separaten Elasticsearch-Cluster.

Mehr darüber, wie die Sync-Engine funktioniert, finden Sie in unserem Beitrag darüber, [warum Git-Sync nicht funktioniert](/blog/why-git-sync-breaks/) und das Content-Ledger-Muster, das es löst.

## Vergleich: Eingebettete vs. Externe Suche

| Fähigkeit | SQL LIKE | SQLite FTS5 | Bleve (eingebettet) | Elasticsearch |
|---|---|---|---|---|
| Tokenisierung | Nein | Ja | Ja | Ja |
| Stemming | Nein | Eingeschränkt | Ja | Ja |
| Fuzzy-Matching | Nein | Nein | Ja | Ja |
| Field-Boosting | Nein | Nein | Ja | Ja |
| Relevanz-Ranking | Nein | Einfach | TF-IDF | BM25 |
| Zusätzlicher Dienst | Nein | Nein | Nein | Ja |
| Speicher-Overhead | Keiner | ~1 MB | ~10 MB | 1–4 GB (JVM) |
| Ops-Komplexität | Keine | Keine | Keine | Hoch |

Elasticsearch gewinnt bei erweiterten Funktionen: Aggregationen, verschachtelte Dokumentabfragen, benutzerdefinierte Analyzer, verteilte Suche über Cluster. Wenn Sie ein Suchprodukt bauen, brauchen Sie es wahrscheinlich.

Aber für Dokumentationssuche — wo der Korpus Tausende von Seiten umfasst, nicht Millionen von Datensätzen — deckt eingebettetes Bleve die Anforderungen mit null operationellem Overhead ab. Sie brauchen keinen separaten Cluster, um Ihre Dokumentation zu durchsuchen.

Wie wir im [Beitrag zur Single-Binary-Architektur](/blog/single-binary-architecture/) behandelt haben, eliminiert das Halten von allem in einem Prozess eine ganze Klasse operationeller Probleme.

## Wonach Benutzer tatsächlich suchen

Wir haben unsere Suchkonfiguration darauf ausgerichtet, wie Menschen tatsächlich Dokumentation durchsuchen:

**Exakte Feature-Namen:** „RBAC", „WebAuthn", „Git Sync" — diese müssen in Titeln und Tags präzise übereinstimmen.

**Konzeptuelle Abfragen:** „Wie richte ich Berechtigungen ein" — diese stützen sich auf Stemming und Textsuche.

**Teilweise Erinnerung:** „Diese Seite über Deploy..." — Fuzzy-Matching und Titel-Boosting helfen, das richtige Ergebnis auch bei unvollständigen Abfragen zu finden.

**Fehlermeldungen:** Benutzer fügen Fehlermeldungen in die Suche ein. Diese profitieren von exaktem Matching mit langen Token-Sequenzen.

Die Standardkonfiguration verarbeitet all das gut. Kein Tuning erforderlich.

## Probieren Sie es aus

Wenn Sie das in Aktion sehen möchten, [installieren Sie DocPlatform](/install/) und erstellen Sie ein paar Seiten. Die Suchleiste in der veröffentlichten Dokumentationsseite verwendet exakt das hier beschriebene System. Geben Sie eine Abfrage ein, vertippen Sie sich absichtlich und beobachten Sie, wie trotzdem gefunden wird, was Sie brauchen.

Die Community Edition enthält alle Suchfunktionen — keine Feature-Einschränkungen, kein „Upgrade für bessere Suche". Der [Leitfaden zur Suchkonfiguration](/docs/guides/search/) behandelt die Details zur Anpassung des Suchverhaltens, falls Sie es brauchen.
