---
title: "Die Zukunft der Dokumentation ist KI-nativ"
description: "Dokumentation wird sich von statischen Seiten zu KI-gepflegten Systemen wandeln. DocPlatform liefert heute 13 MCP-Tools, mit denen KI-Agenten Ihre Dokumentation lesen und schreiben können."
date: "2026-04-13"
author: "Valoryx Team"
tags: ["ai", "mcp", "documentation", "future"]
---

Dokumentation hat ein Pflegeproblem. Sie schreiben eine Anleitung, veröffentlichen sie, und innerhalb von drei Monaten ist sie veraltet. Die API hat sich geändert. Das Konfigurationsformat wurde refaktoriert. Eine Abhängigkeit wurde ersetzt. Die Screenshots zeigen eine Oberfläche, die nicht mehr existiert.

Die Lösung ist nicht „bessere Dokumentation schreiben" oder „eine Dokumentationskultur aufbauen." Teams versuchen das seit Jahrzehnten. Die Lösung ist, Dokumentation bewusst mit dem Code zu verknüpfen, den sie beschreibt — sodass die Dokumentation es mitbekommt, wenn sich der Code ändert.

Das bedeutet KI-native Dokumentation. Nicht „KI schreibt Ihre Dokumentation" (das produziert generischen, seelenlosen Inhalt). Stattdessen: KI überwacht Ihre Codebasis, erkennt, wenn Dokumentation von der Realität abweicht, und markiert es entweder für einen Menschen oder schlägt spezifische Aktualisierungen vor. Der Mensch bleibt für das Urteil in der Schleife; die Maschine übernimmt die Überwachung.

## Das Veralterungsproblem, quantifiziert

Eine Studie von Zhi et al. aus dem Jahr 2023 ergab, dass 68 % der Dokumentationsseiten in aktiven Softwareprojekten mindestens eine faktische Inkonsistenz mit der aktuellen Codebasis enthalten. Die häufigsten Probleme:

- **Veraltete API-Signaturen** — Parameter hinzugefügt oder entfernt, aber Dokumentation nicht aktualisiert
- **Falsche Konfigurationsbeispiele** — Standardwerte geändert, altes Format noch dokumentiert
- **Tote Links** — Seiten umstrukturiert, interne Verweise nicht aktualisiert
- **Fehlende Features** — neue Funktionen hinzugefügt, ohne jegliche Dokumentation

Manuelles Review erkennt diese Probleme langsam, wenn überhaupt. Ein Team von 20 Ingenieuren macht vielleicht einmal im Quartal einen „Docs-Audit" und verbringt eine Woche damit, die Funde zu beheben. Bis der Audit abgeschlossen ist, hat neuer Drift bereits begonnen.

## Was KI-nativ wirklich bedeutet

Eine KI-native Dokumentationsplattform hat drei Eigenschaften:

**1. Maschinenlesbarer Inhalt.** Die Dokumentation ist in einem Format gespeichert, das KI-Tools programmatisch lesen, abfragen und ändern können. Markdown in einem Git-Repository qualifiziert sich. Proprietärer Rich-Text in einer SaaS-Datenbank nicht.

**2. Code-zu-Docs-Verknüpfung.** Die Plattform weiß (oder kann entdecken), welche Dokumentationsseiten welche Teile der Codebasis beschreiben. Wenn sich `auth.go` ändert, kann die Plattform identifizieren, dass `docs/authentication.md` möglicherweise aktualisiert werden muss.

**3. Strukturierter Tool-Zugang.** KI-Agenten können mit der Dokumentation über ein definiertes Protokoll interagieren — nicht durch HTML-Scraping oder Reverse-Engineering von APIs, sondern durch explizite, dokumentierte Tools.

DocPlatform implementiert alle drei heute, unter Verwendung des Model Context Protocol (MCP).

## MCP: Das Protokoll

[MCP](https://modelcontextprotocol.io/) ist ein offener Standard, der von Anthropic entwickelt wurde, um KI-Modelle mit externen Tools und Datenquellen zu verbinden. Anstatt dass jedes KI-Tool individuelle Integrationen mit jeder Plattform baut, definiert MCP eine Standardschnittstelle: Tools (Aktionen, die die KI ausführen kann), Ressourcen (Daten, die die KI lesen kann) und Prompts (Templates für gängige Workflows).

DocPlatform wird mit einem eingebauten MCP-Server ausgeliefert — keine Plugins, kein separater Dienst. Wenn Sie ihn aktivieren, kann jeder MCP-kompatible KI-Client mit Ihrer Dokumentation über 13 zweckgebundene Tools interagieren.

## Die 26 Tools

Hier ist eine Auswahl dessen, was DocPlatforms MCP-Server bereitstellt — die vollständige Referenz aller 26 Tools finden Sie auf der [MCP-Seite](/mcp/):

### Leseoperationen

- **`search_docs`** — Volltextsuche über die gesamte Dokumentation. Gibt passende Seiten mit Relevanzwerten und Ausschnitten zurück. Ein KI-Agent verwendet dies, um die Seite zu finden, die ein bestimmtes Feature beschreibt, bevor er prüft, ob sie noch aktuell ist.

- **`get_page`** — Den vollständigen Inhalt einer bestimmten Seite über ihren Pfad abrufen. Gibt Markdown-Inhalt, Metadaten (Autor, letzte Änderung, Tags) und die Position der Seite im Navigationsbaum zurück.

- **`list_pages`** — Alle Seiten in einem Workspace auflisten, mit optionaler Filterung nach Pfadpräfix oder Tag. Nützlich für KI-Agenten, die Massenaudits durchführen.

- **`get_workspace_info`** — Metadaten über einen Workspace: Name, Theme, Git-Repository-Verbindung, Veröffentlichungsstatus.

### Schreiboperationen

- **`create_page`** — Eine neue Dokumentationsseite erstellen. Nimmt einen Pfad, Titel und Markdown-Inhalt entgegen. Die Seite wird sofort für die Suche indiziert und nach Git committed.

- **`update_page`** — Den Inhalt einer bestehenden Seite ändern. Der KI-Agent liefert das neue Markdown, und DocPlatform kümmert sich um Versionierung, Suchindex-Aktualisierung und Git-Commit.

- **`move_page`** — Eine Seite im Navigationsbaum verschieben. Verarbeitet Pfadaktualisierungen und Redirect-Erstellung.

- **`delete_page`** — Eine Seite entfernen. Entfernt sie aus dem Suchindex und committed die Löschung nach Git.

### Analyseoperationen

- **`check_links`** — Alle internen Links in einer Seite oder einem Workspace überprüfen. Gibt eine Liste defekter Links mit Quellseite und Zielpfad zurück. Ein KI-Agent kann dies nach einer Umstrukturierung ausführen, um tote Verweise zu finden.

- **`check_freshness`** — Letzte Änderungsdaten von Seiten mit Git-Commit-Zeitstempeln der Codeabschnitte vergleichen, die sie beschreiben. Markiert Seiten, die nicht aktualisiert wurden, seit sich ihr entsprechender Code geändert hat.

- **`suggest_updates`** — Ausgehend von einem Code-Diff (z. B. aus einem aktuellen PR) Dokumentationsseiten identifizieren, die wahrscheinlich aktualisiert werden müssen, und spezifische Änderungen vorschlagen.

### Workflow-Operationen

- **`create_review`** — Eine Dokumentationsänderung zur menschlichen Überprüfung einreichen. Erstellt einen Entwurf, der in der Review-Warteschlange erscheint, nicht auf der veröffentlichten Seite.

- **`get_review_status`** — Den Status einer ausstehenden Überprüfung abfragen.

## Praktische Workflows

Diese Tools sind nicht theoretisch. So verwenden Teams sie heute.

### Erkennung veralteter Dokumentation

Eine geplante Aufgabe läuft nächtlich:

```
1. KI-Agent ruft list_pages auf, um alle Dokumentationsseiten zu erhalten
2. Für jede Seite ruft er check_freshness auf, um mit aktuellen Codeänderungen zu vergleichen
3. Als veraltet markierte Seiten werden dem Team gemeldet
4. Für Fälle mit hoher Konfidenz ruft der Agent suggest_updates mit dem relevanten Code-Diff auf
5. Vorschläge gehen über create_review — ein Mensch genehmigt oder lehnt ab
```

Das verwandelt Dokumentationspflege von einer vierteljährlichen Feuerwehrübung in einen kontinuierlichen Prozess. Veraltete Seiten werden innerhalb von 24 Stunden nach der Codeänderung erkannt, die sie veralten ließ.

### PR-ausgelöste Dokumentationsaktualisierungen

Wenn ein Pull Request eine öffentliche API ändert:

```
1. Die CI-Pipeline extrahiert den Diff
2. KI-Agent ruft search_docs auf, um Seiten zu finden, die die geänderte API referenzieren
3. Agent ruft suggest_updates mit dem Diff und passenden Seiten auf
4. Wenn Änderungen unkompliziert sind (Parameterumbenennung, neue Option),
   ruft der Agent create_review mit dem vorgeschlagenen Update auf
5. Die Dokumentationsaktualisierung wird im selben PR-Zyklus wie die Codeänderung ausgeliefert
```

Kein „erstelle ein Follow-up-Ticket zum Aktualisieren der Dokumentation" mehr. Die Dokumentationsaktualisierung ist Teil desselben Workflows.

### Dokumentation neuer Features

Wenn ein Feature ohne Dokumentation gemerged wird (es passiert):

```
1. Agent erkennt neue exportierte Funktionen/Endpoints ohne passende Dokumentationsseite
2. Agent ruft create_page mit einem Gerüst auf: Funktionssignatur, Parameterbeschreibungen,
   ein Platzhalter-Beispiel
3. Erstellt einen Review, damit ein Mensch die Erklärung ausformuliert und reale Beispiele hinzufügt
```

Der Mensch schreibt immer noch die Erzählung. Aber das Gerüst — die korrekten Funktionssignaturen, die Parametertypen, die Rückgabewerte — kommt direkt aus dem Code. Keine Copy-Paste-Fehler, kein Vergessen bei Signaturänderungen.

## Was das NICHT ist

Klarheit über die Grenzen:

**Das ist nicht „KI schreibt Ihre Dokumentation."** KI-generierte Dokumentation, die nie von einem Menschen überprüft wird, ist schlimmer als keine Dokumentation. Sie ist selbstsicher falsch, generisch formuliert und bringt Menschen dazu, Ihrer Dokumentation zu misstrauen. Die MCP-Tools erstellen Entwürfe und Vorschläge — Menschen überprüfen und genehmigen.

**Das ist kein Ersatz für technische Redakteure.** Gute Dokumentation erfordert Urteilsvermögen: was erklären, was weglassen, in welcher Reihenfolge Konzepte präsentieren, wie ein Beispiel schreiben, das wirklich hilft. KI hat dieses Urteilsvermögen nicht. Sie hat Mustererkennung.

**Das ist keine Magie.** Das `check_freshness`-Tool funktioniert, weil Dokumentationsseiten und Codedateien durch Pfadkonventionen und explizite Metadaten verknüpft werden können. Wenn Ihre Dokumentation und Ihr Code keine Beziehungsstruktur haben, kann das Tool keine ableiten.

Was es IST: ein Überwachungssystem für Dokumentationsqualität. Es beobachtet, markiert, schlägt vor. Menschen entscheiden.

## Warum das jetzt relevant ist

Drei Dinge sind zusammengekommen, um dies zu ermöglichen:

**MCP-Standardisierung.** Vor MCP brauchte jedes KI-Tool individuelle Integrationen. Jetzt gibt es ein einziges Protokoll. Claude, Cursor, VS Code mit Copilot — sie alle sprechen MCP. Eine Integration bauen, überall funktionieren.

**KI-Modelle, die über Code nachdenken können.** Aktuelle Modelle können einen Code-Diff lesen und verstehen, was sich semantisch geändert hat — nicht nur syntaktisch. „Diese Funktion akzeptiert jetzt einen optionalen `timeout`-Parameter" ist etwas, das ein Modell zuverlässig aus einem Diff extrahieren kann.

**Dokumentationsplattformen, die Inhalte als Code speichern.** Markdown in Git-Repositories bedeutet, dass KI-Agenten Dokumentation mit denselben Tools lesen und schreiben können, die sie für Code verwenden. Keine proprietären APIs, kein Screen-Scraping.

DocPlatform befindet sich am Schnittpunkt aller drei. Inhalte in Git (maschinenlesbar), MCP-Server eingebaut (strukturierter Tool-Zugang) und code-bewusste Werkzeuge (Verknüpfung zwischen Dokumentation und Codebasis).

## Erste Schritte

Der MCP-Server ist in jeder DocPlatform-Installation enthalten — Community Edition und Cloud.

Um ihn zu aktivieren:

```bash
docplatform serve --mcp
```

Dann richten Sie Ihren KI-Client darauf. In Claude Desktop fügen Sie zu Ihrer MCP-Konfiguration hinzu:

```json
{
  "mcpServers": {
    "docplatform": {
      "url": "http://localhost:3000/mcp"
    }
  }
}
```

Die vollständige Einrichtungsanleitung, einschließlich Authentifizierung und Workspace-Scoping, finden Sie in der [MCP-Dokumentation](/mcp/).

Wenn Sie sehen möchten, wie die MCP-Tools in der Praxis funktionieren, geht unser früherer Beitrag über [MCP für Dokumentation](/blog/mcp-documentation-guide/) spezifische Beispiele durch.

Die Zukunft der Dokumentation ist nicht, dass KI Autoren ersetzt. Es ist, dass KI die Lichter anlässt — Veralterung erkennt, Drift markiert, Links pflegt — damit sich Autoren auf die Arbeit konzentrieren können, die wirklich menschliches Urteilsvermögen erfordert.

[Installieren Sie DocPlatform](/install/) und verbinden Sie Ihren ersten KI-Agenten mit Ihrer Dokumentation.
