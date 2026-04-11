---
title: "Wie man Dokumentation aktuell hält"
description: "Dokumentation veraltet, weil die Aktualisierung von Codeänderungen entkoppelt ist. Drei Ansätze, die funktionieren: Git-Sync, MCP-gestützte Reviews und PR-Workflows."
date: "2026-03-26"
author: "Valoryx Team"
tags: ["documentation", "maintenance", "ai", "git"]
---

Jedes Engineering-Team hat dasselbe Dokumentationsproblem. Jemand schreibt gründliche Dokumentation während eines Launches. Sechs Monate später hat sich die API geändert, das Konfigurationsformat ist anders, und drei Seiten verweisen auf ein Feature, das umbenannt wurde. Niemand hat die Dokumentation aktualisiert, weil das Aktualisieren von Dokumentation eine separate Aufgabe vom Code-Schreiben ist, und separate Aufgaben werden vergessen.

Der übliche Ratschlag — „Machen Sie Dokumentation zum Teil Ihrer Kultur" — funktioniert nicht. Kultur überlebt keinen Termindruck. Was funktioniert, ist Dokumentationsaktualisierungen zum Teil bestehender Workflows zu machen, sodass sie automatisch oder mit minimalem Aufwand passieren.

Hier sind drei Ansätze, die Dokumentationsveralterung tatsächlich reduzieren, jeder auf einen anderen Teil des Problems ausgerichtet.

## Ansatz 1: Git-Sync — Dokumentation ändert sich mit dem Code

Der zuverlässigste Weg, Dokumentation aktuell zu halten, ist sie im selben Repository wie den Code zu speichern, den sie beschreibt, oder in einem verbundenen Repository, das bidirektional synchronisiert.

Wenn Dokumentation in Git lebt, können Sie:

- **Dokumentationsaktualisierungen in PRs erfordern.** Fügen Sie einen CI-Check oder eine Review-Regel hinzu: Wenn Code in `/api/` sich ändert, muss der PR auch Dateien in `/docs/api/` berühren. Das garantiert keine Qualität, aber es garantiert, dass jemand zumindest die relevante Dokumentation angeschaut hat.

- **`git log` verwenden, um Drift zu finden.** Vergleichen Sie die letzten Änderungsdaten von Code-Dateien und ihren entsprechenden Dokumentationsseiten. Wenn `auth_handler.go` vor 3 Monaten aktualisiert wurde, aber `docs/authentication.md` sich seit 8 Monaten nicht geändert hat, ist das ein Veralterungssignal.

- **Dokumentation im selben Diff reviewen.** Wenn ein Entwickler ändert, wie Paginierung funktioniert, sieht der Reviewer sowohl die Codeänderung als auch die Dokumentationsaktualisierung in einem Pull Request. Kontext bleibt erhalten. Der Reviewer kann überprüfen, ob die Dokumentation zur Implementierung passt.

Die Herausforderung bei Git-basierter Dokumentation ist, dass nicht jeder in einem Dokumentationsteam Git verwendet. Technische Redakteure, Produktmanager und Support-Ingenieure bevorzugen oft einen Web-Editor. Hier wird [bidirektionaler Git-Sync](/docs/guides/git-integration/) wichtig — er lässt Web-Editoren und Git-Benutzer an denselben Inhalten arbeiten, ohne dass ein Workflow den anderen stört.

Das Content-Ledger-Muster von Valoryx löst dies, indem jede Bearbeitung unabhängig vom Ursprung (Web-Oberfläche, Git-Push, API, MCP-Tool) verfolgt und Änderungen automatisch abgeglichen werden. Siehe [Wie bidirektionaler Git-Sync funktioniert](/blog/bidirectional-git-sync/) für die technischen Details.

## Ansatz 2: MCP-gestütztes Review — KI markiert veraltete Inhalte

Manuelle Audits der Dokumentation sind gründlich, aber selten. Niemand hat Zeit, jede Seite vierteljährlich zu lesen und gegen die aktuelle Codebasis zu prüfen. KI-Assistenten mit strukturiertem Zugriff auf Ihre Dokumentation können dies kontinuierlich tun.

Mit [Model Context Protocol (MCP)](/mcp/) können Sie einen KI-Assistenten mit Ihrer Dokumentationsinstanz verbinden und gezielte Audits durchführen. So sieht das in der Praxis aus.

### Seiten finden, die veraltete Endpoints referenzieren

```
Prompt: "Durchsuche alle Seiten nach Verweisen auf /api/v1/ — wir haben 
letzten Monat auf /api/v2/ migriert. Liste jede Seite auf, die noch v1 erwähnt."
```

Der Assistent ruft das MCP-Tool `search_pages` auf, findet jedes Vorkommen und gibt eine Liste mit Seitenpfaden und umgebendem Kontext zurück. Was einen Menschen 30 Minuten Grep-und-Lesen kosten würde, erledigt die KI in etwa 10 Sekunden.

### Terminologie-Drift erkennen

```
Prompt: "Finde alle Seiten, die den Begriff 'Workspace-Gruppe' verwenden. Wir 
haben das in v3.2 in 'Organisation' umbenannt. Liste sie auf."
```

Gleiches Tool, andere Abfrage. Der Assistent findet jede Instanz veralteter Terminologie. Sie überprüfen die Liste und entscheiden, welche Seiten aktualisiert werden.

### Veralterungsbericht generieren

```
Prompt: "Liste alle Seiten im API-Referenz-Workspace auf, die in den letzten 
60 Tagen nicht aktualisiert wurden, sortiert nach Alter."
```

Der Assistent ruft `search_recent` auf und vergleicht mit dem vollständigen Seitenbaum. Sie erhalten eine priorisierte Liste der Seiten, die am wahrscheinlichsten veraltet sind.

### Aktualisierungen durchführen

Sobald Sie veraltete Inhalte identifiziert haben, kann die KI Aktualisierungen entwerfen:

```
Prompt: "Lies den aktuellen Authentifizierungsleitfaden. Der Login-Endpoint 
akzeptiert jetzt neben Passwörtern auch Passkeys. Aktualisiere den Leitfaden 
für beide Methoden, behalte die bestehende Struktur bei."
```

Der Assistent liest die Seite über `get_page`, entwirft die Aktualisierung und wendet sie über `update_page` an. Die Bearbeitung erscheint in der Revisionshistorie und, wenn Git-Sync konfiguriert ist, als Commit, den Sie in einem Pull Request überprüfen können.

Die Kernererkenntnis ist, dass [MCP die KI zu einem Teilnehmer an Ihrem Docs-Workflow macht](/blog/mcp-documentation-guide/), nicht zu einem losgelösten Textgenerator. Sie liest Ihre tatsächlichen Inhalte, nimmt Änderungen über dasselbe System vor, das Ihr Team verwendet, und hinterlässt einen Audit Trail.

## Ansatz 3: PR-basierte Dokumentationsreviews

Der dritte Ansatz ist organisatorisch: Verwenden Sie denselben Review-Prozess für Dokumentation, den Sie für Code verwenden.

### Der Dokumentations-Review-PR

Wenn ein Feature ausgeliefert wird, erstellen Sie eine Folgeaufgabe: „Dokumentation für Feature X aktualisieren." Diese Aufgabe resultiert in einem Pull Request, der:

1. Die relevanten Dokumentationsseiten aktualisiert
2. Von jemandem reviewed wird, der das Feature versteht
3. Durch dieselbe CI-Pipeline wie Codeänderungen läuft

Das funktioniert, weil es kein neuer Prozess ist. Ihr Team reviewed bereits PRs. Dokumentationsaktualisierungen zum selben Workflow hinzuzufügen bedeutet, dass sie dieselbe Aufmerksamkeit bekommen.

### Automatisierte Veralterungsprüfungen in CI

Sie können Veralterungserkennung in Ihrer CI-Pipeline automatisieren. Ein einfacher Ansatz:

```bash
#!/bin/bash
# Dokumentation finden, die seit 90 Tagen nicht aktualisiert wurde
STALE_THRESHOLD=$(date -d '90 days ago' +%s)

for doc in docs/**/*.md; do
  LAST_MODIFIED=$(git log -1 --format="%ct" -- "$doc")
  if [ "$LAST_MODIFIED" -lt "$STALE_THRESHOLD" ]; then
    echo "VERALTET: $doc (zuletzt aktualisiert $(git log -1 --format='%ci' -- "$doc"))"
  fi
done
```

Führen Sie das wöchentlich in CI aus. Wenn veraltete Dokumentation gefunden wird, erstellen Sie automatisch ein Issue. Das verwandelt „Dokumentation könnte veraltet sein" von einer vagen Sorge in eine konkrete, nachverfolgte Aufgabe.

### Review-Rotation

Weisen Sie Dokumentationsreviews einem Rotationsplan zu, genauso wie Sie On-Call-Rotationen zuweisen. Jede Woche überprüft eine Person 5–10 Seiten. Nicht die gesamte Seite — nur einen Ausschnitt. Über ein Quartal wird die gesamte Dokumentation durchgesehen.

Das ist unspektakuläre Arbeit. Aber es ist der einzige Weg, die Art von Veralterung zu erkennen, die automatisierte Tools übersehen: Seiten, die technisch korrekt aber schlecht organisiert sind, Beispiele, die veraltete Muster verwenden, Anleitungen, die Kontext voraussetzen, den der Leser nicht hat.

## Alle drei kombinieren

Diese Ansätze funktionieren am besten zusammen:

- **Git-Sync** erkennt Drift an der Quelle — wenn sich Code ändert, ist die Dokumentation im selben PR
- **MCP-gestütztes Review** erkennt, was Git-Sync übersieht — Terminologieänderungen, veraltete Verweise, alte Seiten
- **PR-basierte Reviews** erkennen, was KI übersieht — strukturelle Probleme, unklares Schreiben, fehlender Kontext

Ein praktischer wöchentlicher Workflow:

1. **Montag:** Einen MCP-Audit der wichtigsten Dokumentationsbereiche durchführen (API-Referenz, Erste-Schritte-Anleitung). Aktualisierungen überprüfen und mergen.
2. **Unter der Woche:** Dokumentationsaktualisierungen in Code-PRs erfordern, die nutzerrelevantes Verhalten betreffen.
3. **Freitag:** Die Person in der Rotationsschicht liest 5–10 Seiten und erstellt Issues für alles, was Aufmerksamkeit braucht.

Das erfordert kein dediziertes Dokumentationsteam. Es verteilt die Arbeit auf Personen, die den Inhalt bereits verstehen. Die Werkzeuge — [Git-Sync](/docs/guides/git-integration/), [MCP](/mcp/), CI-Checks — reduzieren den Aufwand pro Person auf ein nachhaltiges Maß.

## Erste Schritte

Wenn Ihre Dokumentation bereits veraltet ist, beginnen Sie mit den meistbesuchten Seiten. Laut der [Splunk Developer Survey](https://www.splunk.com/en_us/form/state-of-observability.html) folgen die meisten Dokumentationsseiten einer Potenzgesetzverteilung — 10 % der Seiten erhalten 80 % des Traffics. Beheben Sie diese zuerst.

Dann richten Sie die Infrastruktur ein, um zukünftige Veralterung zu verhindern:

1. [Valoryx installieren](/install/) und Ihre Dokumentation mit einem Git-Repository verbinden
2. MCP für Ihren KI-Assistenten konfigurieren, damit Sie Audits bei Bedarf durchführen können
3. Eine Veralterungsprüfung zu Ihrer CI-Pipeline hinzufügen
4. Eine leichtgewichtige Review-Rotation starten

Dokumentation veraltet, weil die Feedbackschleife zwischen Codeänderungen und Dokumentationsaktualisierungen unterbrochen ist. Git-Sync strafft die Schleife an der Quelle. MCP gibt Ihnen ein schnelles Audit-Werkzeug. PR-basierte Reviews fügen menschliches Urteilsvermögen hinzu. Zusammen machen sie „Dokumentation aktuell halten" zu einem lösbaren Problem statt einer verlorenen Schlacht.
