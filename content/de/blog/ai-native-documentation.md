---
title: "Die Zukunft der Dokumentation ist KI-nativ"
description: "Dokumentation wird sich von statischen Seiten zu KI-gepflegten Systemen wandeln. DocPlatform liefert heute 26 MCP-Tools, mit denen KI-Agenten Ihre Dokumentation lesen und schreiben können."
date: "2026-04-13"
author: "Valoryx Team"
tags: ["ai", "mcp", "documentation", "future"]
---

Dokumentation hat ein Pflegeproblem. Sie schreiben eine Anleitung, veröffentlichen sie, und innerhalb von drei Monaten ist sie veraltet. Die API hat sich geändert. Das Konfigurationsformat wurde refaktoriert. Eine Abhängigkeit wurde ersetzt. Die Screenshots zeigen eine Oberfläche, die nicht mehr existiert.

Die Lösung ist nicht „bessere Dokumentation schreiben" oder „eine Dokumentationskultur aufbauen." Teams versuchen das seit Jahrzehnten. Die Lösung ist, Dokumentation bewusst mit dem Code zu verknüpfen, den sie beschreibt — sodass die Dokumentation es mitbekommt, wenn sich der Code ändert.

Das bedeutet KI-native Dokumentation. Nicht „KI schreibt Ihre Dokumentation" (das produziert generischen, seelenlosen Inhalt). Stattdessen: KI überwacht Ihre Codebasis, erkennt, wenn Dokumentation von der Realität abweicht, und markiert es entweder für einen Menschen oder schlägt spezifische Aktualisierungen vor. Der Mensch bleibt für das Urteil in der Schleife; die Maschine übernimmt die Überwachung.

## Das Veralterungsproblem, quantifiziert

Prüfen Sie die Dokumentation eines beliebigen aktiven Softwareprojekts, und Sie werden feststellen, dass ein großer Teil der Seiten mindestens eine faktische Inkonsistenz mit der aktuellen Codebasis enthält. Die häufigsten Probleme:

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

DocPlatform liefert heute die erste und die dritte Eigenschaft — Markdown, das mit Git synchronisiert wird, plus ein eingebauter MCP-Server. Die zweite, die Code-zu-Docs-Verknüpfung, bauen Sie mit Konventionen darauf auf: Wenn Dokumentation und Code in verbundenen Repositories leben, kann ein KI-Agent mit Zugriff auf beide die Verbindung selbst herstellen.

## MCP: Das Protokoll

[MCP](https://modelcontextprotocol.io/) ist ein offener Standard, der von Anthropic entwickelt wurde, um KI-Modelle mit externen Tools und Datenquellen zu verbinden. Anstatt dass jedes KI-Tool individuelle Integrationen mit jeder Plattform baut, definiert MCP eine Standardschnittstelle: Tools (Aktionen, die die KI ausführen kann), Ressourcen (Daten, die die KI lesen kann) und Prompts (Templates für gängige Workflows).

DocPlatform wird mit einem eingebauten MCP-Server ausgeliefert — keine Plugins, kein separater Dienst. Wenn Sie ihn aktivieren, kann jeder MCP-kompatible KI-Client mit Ihrer Dokumentation über 26 zweckgebundene Tools interagieren.

## Die 26 Tools

Hier ist eine Auswahl dessen, was DocPlatforms MCP-Server bereitstellt — die vollständige Referenz aller 26 Tools finden Sie auf der [MCP-Seite](/mcp/). Jedes Tool trägt den Namespace `docplatform_*`, sodass es nie mit anderen MCP-Servern in Ihrem Client kollidiert.

### Leseoperationen

- **`docplatform_search`** — Volltextsuche über den Workspace, mit Fuzzy-Matching und nach Relevanz sortierten Ergebnissen. Ein KI-Agent verwendet dies, um die Seite zu finden, die ein bestimmtes Feature beschreibt, bevor er prüft, ob sie noch aktuell ist.

- **`docplatform_read_page`** — Den vollständigen Inhalt einer bestimmten Seite über ihren Pfad abrufen: Markdown-Inhalt plus Metadaten.

- **`docplatform_get_context`** — Das RAG-Arbeitspferd: liefert eine Seite zusammen mit ihrem Elternknoten, ihren Geschwistern und den Zielen ihrer Wikilinks in einem Aufruf — der Agent bekommt den umgebenden Kontext ohne fünf Roundtrips.

- **`docplatform_list_pages`** / **`docplatform_get_tree`** — Die Seiten eines Workspace und seinen Navigationsbaum aufzählen. Nützlich für KI-Agenten, die Massenaudits durchführen.

### Schreiboperationen

- **`docplatform_write_page`** — Eine Seite schreiben: erstellt sie, wenn sie nicht existiert, aktualisiert sie andernfalls. Die Seite wird für die Suche indiziert und, mit konfigurierter Git-Synchronisation, nach Git committed.

- **`docplatform_update_page`** — Den Inhalt einer bestehenden Seite ändern (schlägt fehl, statt zu erstellen — für Fälle, in denen die Seite bereits existieren muss).

- **`docplatform_move_page`** — Eine Seite an einen neuen Pfad im Baum verschieben.

- **`docplatform_delete_page`** — Eine Seite entfernen.

### Analyseoperationen

- **`docplatform_validate_links`** — Interne Links und Wikilinks überprüfen. Gibt defekte Ziele mit ihren Quellseiten zurück. Ein KI-Agent kann dies nach einer Umstrukturierung ausführen, um tote Verweise zu finden.

- **`docplatform_quality_scan`** — Inhalte auf Qualitätsprobleme prüfen — das Rohmaterial für einen agentengenerierten Audit-Bericht.

### Kollaborationsoperationen

- **`docplatform_get_activity`** — Der Feed der letzten Aktivitäten: wer hat was wann geändert. Der Ausgangspunkt für Veralterungsanalysen.

- **`docplatform_list_comments`** / **`docplatform_add_comment`** — Seitendiskussionen lesen und sich daran beteiligen, damit ein Agent einen Fund direkt auf der betroffenen Seite markieren kann.

## Praktische Workflows

Diese Tools fügen sich zu echten Workflows zusammen. So sieht das in der Praxis aus.

### Erkennung veralteter Dokumentation

Ein geplanter Agentenlauf (ein Cron-Job, der einen MCP-verbundenen Assistenten steuert):

```
1. Agent ruft docplatform_get_tree auf, um alle Dokumentationsseiten aufzuzählen
2. Ruft docplatform_get_activity auf, um zu sehen, was sich kürzlich geändert hat —
   Seiten ohne Aktivität, deren Themengebiet sich weiterbewegt hat, sind Kandidaten
3. Für jeden Kandidaten ruft er docplatform_read_page auf und vergleicht den Inhalt
   mit dem aktuellen Code (der Agent hat auch Repo-Zugriff)
4. Funde werden mit docplatform_add_comment auf der betroffenen Seite markiert —
   ein Mensch prüft und entscheidet
```

Das verwandelt Dokumentationspflege von einer vierteljährlichen Feuerwehrübung in einen kontinuierlichen Prozess.

### PR-ausgelöste Dokumentationsaktualisierungen

Wenn ein Pull Request eine öffentliche API ändert:

```
1. Die CI-Pipeline extrahiert den Diff
2. KI-Agent ruft docplatform_search auf, um Seiten zu finden, die die geänderte API referenzieren
3. Agent liest jeden Treffer mit docplatform_read_page und entwirft die Aktualisierung
4. Mit konfigurierter Git-Synchronisation wird die docplatform_write_page-Änderung
   des Agenten zu einem Commit — reviewbar im selben PR-Zyklus wie die Codeänderung
```

Kein „erstelle ein Follow-up-Ticket zum Aktualisieren der Dokumentation" mehr. Die Dokumentationsaktualisierung ist Teil desselben Workflows.

### Dokumentation neuer Features

Wenn ein Feature ohne Dokumentation gemerged wird (es passiert):

```
1. Agent erkennt neue exportierte Funktionen/Endpoints ohne passende Dokumentationsseite
   (docplatform_search liefert für die neuen Namen keine Treffer)
2. Agent ruft docplatform_write_page mit einem Gerüst auf: Funktionssignatur,
   Parameterbeschreibungen, ein Platzhalter-Beispiel
3. Danach folgt die menschliche Ausarbeitung — der Entwurf wird im Seitenverlauf
   nachverfolgt und ist über die Git-Synchronisation als Commit reviewbar
```

Der Mensch schreibt immer noch die Erzählung. Aber das Gerüst — die korrekten Funktionssignaturen, die Parametertypen, die Rückgabewerte — kommt direkt aus dem Code. Keine Copy-Paste-Fehler, kein Vergessen bei Signaturänderungen.

## Was das NICHT ist

Klarheit über die Grenzen:

**Das ist nicht „KI schreibt Ihre Dokumentation."** KI-generierte Dokumentation, die nie von einem Menschen überprüft wird, ist schlimmer als keine Dokumentation. Sie ist selbstsicher falsch, generisch formuliert und bringt Menschen dazu, Ihrer Dokumentation zu misstrauen. Die MCP-Tools erstellen Entwürfe und Vorschläge — Menschen überprüfen und genehmigen.

**Das ist kein Ersatz für technische Redakteure.** Gute Dokumentation erfordert Urteilsvermögen: was erklären, was weglassen, in welcher Reihenfolge Konzepte präsentieren, wie ein Beispiel schreiben, das wirklich hilft. KI hat dieses Urteilsvermögen nicht. Sie hat Mustererkennung.

**Das ist keine Magie.** Veralterungserkennung funktioniert, weil Dokumentationsseiten und Codedateien durch Pfadkonventionen und Repository-Struktur verknüpft werden können. Wenn Ihre Dokumentation und Ihr Code keine Beziehungsstruktur haben, kann der Agent keine ableiten.

Was es IST: ein Überwachungssystem für Dokumentationsqualität. Es beobachtet, markiert, schlägt vor. Menschen entscheiden.

## Warum das jetzt relevant ist

Drei Dinge sind zusammengekommen, um dies zu ermöglichen:

**MCP-Standardisierung.** Vor MCP brauchte jedes KI-Tool individuelle Integrationen. Jetzt gibt es ein einziges Protokoll. Claude, Cursor, VS Code mit Copilot — sie alle sprechen MCP. Eine Integration bauen, überall funktionieren.

**KI-Modelle, die über Code nachdenken können.** Aktuelle Modelle können einen Code-Diff lesen und verstehen, was sich semantisch geändert hat — nicht nur syntaktisch. „Diese Funktion akzeptiert jetzt einen optionalen `timeout`-Parameter" ist etwas, das ein Modell zuverlässig aus einem Diff extrahieren kann.

**Dokumentationsplattformen, die Inhalte als Code speichern.** Markdown in Git-Repositories bedeutet, dass KI-Agenten Dokumentation mit denselben Tools lesen und schreiben können, die sie für Code verwenden. Keine proprietären APIs, kein Screen-Scraping.

DocPlatform befindet sich am Schnittpunkt aller drei. Inhalte in Git (maschinenlesbar), MCP-Server eingebaut (strukturierter Tool-Zugang) und code-bewusste Werkzeuge (Verknüpfung zwischen Dokumentation und Codebasis).

## Erste Schritte

Der MCP-Server ist in jeder DocPlatform-Installation enthalten. Erstellen Sie einen API Key (**Workspace Settings → API Keys**) und richten Sie Ihren KI-Client auf das `docplatform`-Binary. In Claude Desktop fügen Sie zu `claude_desktop_config.json` hinzu:

```json
{
  "mcpServers": {
    "docplatform": {
      "command": "docplatform",
      "args": ["mcp", "--workspace", "my-docs", "--api-key", "dp_live_abc123"]
    }
  }
}
```

Für Remote-Setups gibt es außerdem einen Streamable-HTTP-Transport (`docplatform mcp-server`, der `/mcp` standardmäßig auf Port 8081 bereitstellt). Die vollständige Einrichtungsanleitung, einschließlich Authentifizierung und Workspace-Scoping, finden Sie in der [MCP-Dokumentation](/mcp/).

Wenn Sie sehen möchten, wie die MCP-Tools in der Praxis funktionieren, geht unser früherer Beitrag über [MCP für Dokumentation](/blog/mcp-documentation-guide/) spezifische Beispiele durch.

Die Zukunft der Dokumentation ist nicht, dass KI Autoren ersetzt. Es ist, dass KI die Lichter anlässt — Veralterung erkennt, Drift markiert, Links pflegt — damit sich Autoren auf die Arbeit konzentrieren können, die wirklich menschliches Urteilsvermögen erfordert.

[Installieren Sie DocPlatform](/install/) und verbinden Sie Ihren ersten KI-Agenten mit Ihrer Dokumentation.
