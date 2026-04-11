---
title: "Wie bidirektionaler Git-Sync funktioniert"
description: "Die meisten Dokumentationstools behaupten Git-Integration, scheitern aber bei Konflikten. So macht das Content-Ledger-Muster echten bidirektionalen Sync zuverlässig."
date: "2026-03-19"
author: "Valoryx Team"
tags: ["git-sync", "architecture", "documentation"]
---

Jede Dokumentationsplattform mit einer Git-Integrationsseite macht dasselbe Versprechen: Ihre Dokumentation lebt in Git, Ihr Team bearbeitet im Browser, und alles bleibt synchron. In der Praxis sind die meisten dieser Integrationen Einweg-Spiegel, die auseinanderfallen, sobald zwei Personen aus verschiedenen Richtungen bearbeiten.

Wir haben in einem [früheren Beitrag](/blog/why-git-sync-breaks/) geschrieben, warum das passiert. Dieser geht tiefer in die Lösung: wie Valoryx bidirektionalen Sync mit dem Content-Ledger-Muster implementiert und warum dieser Ansatz die Szenarien bewältigt, an denen andere Tools scheitern.

## Das Kernproblem

Ein webbasierter Editor und ein Git-Repository haben grundlegend unterschiedliche Konsistenzmodelle.

In einem Web-Editor sind Speichervorgänge sofort und atomar. Sie klicken auf Speichern, der Inhalt wird persistiert, und jeder, der die Seite lädt, sieht Ihre Version. Es gibt kein Konzept von „Staging" oder „Committen" — der Schreibvorgang ist die Veröffentlichung.

In Git werden Änderungen in Commits gebündelt, Commits werden zu einem Remote gepusht, und der Remote muss von anderen Teilnehmern gefetcht und gemerged werden. Es gibt eine inhärente Verzögerung zwischen „Ich habe eine Änderung gemacht" und „Alle sehen meine Änderung."

Wenn Sie beide Modelle kombinieren — einen Web-Editor und ein Git-Repository, die auf denselben Inhalt zeigen — schaffen Sie ein Zeitfenster, in dem zwei Personen widersprüchliche Bearbeitungen vornehmen können, ohne voneinander zu wissen. Person A bearbeitet im Browser. Person B pusht einen Commit von VS Code. Keiner weiß vom anderen, bis der Sync läuft, und dann muss eine Seite nachgeben.

Die meisten Plattformen lösen das, indem sie einen Gewinner bestimmen: Entweder gewinnt immer die Datenbank (Wiki.js) oder das Git-Repository gewinnt immer (die meisten Static-Site-Generatoren). Beide Ansätze verlieren still Daten.

## Das Content-Ledger-Muster

Das Content Ledger ist ein append-only Log jeder Inhaltsänderung, unabhängig davon, woher sie stammt. Stellen Sie es sich vor wie ein Write-Ahead-Log in einer Datenbank, aber für Dokumentationsbearbeitungen.

Jede Änderung — ob sie vom Web-Editor, der API, einem MCP-Tool-Aufruf oder einem Git-Push kommt — wird als Ledger-Eintrag aufgezeichnet, bevor sie angewendet wird. Jeder Eintrag enthält:

- **Zeitstempel** — wann die Änderung vorgenommen wurde
- **Ursprung** — woher sie kam (Web, Git, API, MCP)
- **Seitenpfad** — welche Seite betroffen war
- **Operation** — Erstellen, Aktualisieren, Verschieben, Löschen
- **Inhalts-Hash** — SHA-256 des neuen Inhalts
- **Eltern-Hash** — SHA-256 des Inhalts, auf dem diese Änderung basierte

Der Eltern-Hash ist die entscheidende Innovation. Er erstellt eine Kausalitätskette, ähnlich wie [Git-Commits ihren Eltern-Commit referenzieren](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects). Wenn zwei Änderungen denselben Eltern-Hash aber unterschiedliche Inhalts-Hashes haben, liegt ein Konflikt vor — und Sie wissen davon, bevor eine der Änderungen angewendet wird.

## Wie der Sync funktioniert: Schritt für Schritt

Hier ist, was während eines Sync-Zyklus passiert. Valoryx führt dies automatisch in einem konfigurierbaren Intervall aus (Standard: 30 Sekunden) oder auf Anforderung, wenn ein Benutzer es auslöst.

### Schritt 1: Ausstehende Änderungen sammeln

Die Sync-Engine liest alle Ledger-Einträge seit dem letzten erfolgreichen Sync. Dies sind lokale Änderungen, die noch nicht nach Git gepusht wurden.

### Schritt 2: Remote-Änderungen abrufen

Die Engine führt `git fetch` aus, um neue Commits vom Remote-Repository zu erhalten. Sie vergleicht dann den Remote HEAD mit dem lokalen Sync-Zeiger, um eingehende Änderungen zu identifizieren.

### Schritt 3: Abgleich

Für jede Seite, die Änderungen auf beiden Seiten hat (lokale Ledger-Einträge UND Remote-Git-Commits), prüft die Engine die Eltern-Hashes:

- **Keine Überschneidung:** Die lokale Änderung basierte auf derselben Version, die Git hat. Fast-Forward-Merge — beide Änderungen der Reihe nach anwenden.
- **Divergiert, kein Konflikt:** Beide Seiten haben verschiedene Seiten geändert. Beide Änderungssätze unabhängig anwenden.
- **Divergiert, selbe Seite:** Beide Seiten haben dieselbe Seite geändert. Das ist ein echter Konflikt.

### Schritt 4: Konfliktlösung

Wenn ein echter Konflikt erkannt wird, wählt Valoryx nicht still einen Gewinner. Stattdessen:

1. Beide Versionen im Ledger bewahren
2. Die Seite als „In Konflikt" in der Oberfläche markieren
3. Einen Diff zwischen den beiden Versionen anzeigen
4. Einem Menschen die Wahl lassen, welche Version beibehalten wird, oder sie manuell zusammenführen

Das ist dasselbe Modell wie `git merge` mit Konflikten — nur dass es über die Web-Oberfläche funktioniert, sodass nicht-technische Redakteure Konflikte lösen können, ohne Git-Befehle zu lernen.

### Schritt 5: Committen und Pushen

Nach dem Abgleich werden lokale Änderungen in das Git-Repository committed und gepusht. Die Commit-Nachricht enthält den Ursprung jeder Änderung (Web-Bearbeitung, API-Aufruf usw.), sodass Ihre Git-Historie Ihnen sagt, nicht nur was sich geändert hat, sondern wie.

## Was das in der Praxis aussieht

Betrachten Sie dieses reale Szenario. Ein Entwickler aktualisiert die API-Authentifizierungsdokumentation in VS Code und pusht zum Repository. Gleichzeitig bearbeitet ein technischer Redakteur die Einleitung derselben Seite im Valoryx Web-Editor.

Mit einem Einweg-Sync-Tool überschreibt eine Bearbeitung die andere. Mit dem Content Ledger:

1. Der Push des Entwicklers erstellt eine Remote-Änderung (neuer Commit auf der Git-Seite)
2. Das Speichern des Redakteurs erstellt einen lokalen Ledger-Eintrag (neue Mutation auf der Web-Seite)
3. Der Sync läuft, erkennt, dass beide Änderungen dieselbe Seite betreffen
4. Die Eltern-Hashes divergieren — es ist ein echter Konflikt
5. Die Seite wird markiert, beide Versionen bleiben erhalten
6. Der Redakteur sieht eine Benachrichtigung: „Diese Seite hat einen Sync-Konflikt" mit einer Diff-Ansicht
7. Der Redakteur führt die Änderungen zusammen (der Entwickler hat einen Code-Block korrigiert, der Redakteur hat die Einleitung umgeschrieben — beide Bearbeitungen sind gültig)
8. Die zusammengeführte Version wird committed und gepusht

Kein Datenverlust. Kein stilles Überschreiben. Die Zusammenführung passierte über eine Web-Oberfläche, nicht ein Terminal.

## Vergleich mit Einweg-Ansätzen

| Szenario | Einweg (DB gewinnt) | Einweg (Git gewinnt) | Content Ledger |
|----------|---------------------|----------------------|----------------|
| Web-Bearbeitung + Git-Push (selbe Seite) | Git-Änderung verloren | Web-Änderung verloren | Konflikt aufgezeigt, beide bewahrt |
| Web-Bearbeitung + Git-Push (verschiedene Seiten) | Funktioniert | Funktioniert | Funktioniert |
| Schnelle Web-Bearbeitungen | Funktioniert | Funktioniert | Funktioniert (in einzelnen Commit zusammengefasst) |
| Offline-Git-Bearbeitungen, Bulk-Push | Einige Änderungen verloren | Funktioniert | Funktioniert |
| Git-Branch-Merge in main | Unvorhersehbar | Funktioniert | Funktioniert (behandelt Merge-Commit wie jeden anderen) |
| Umbenennung/Verschiebung im Web + Bearbeitung in Git | Pfad-Diskrepanz, Sync bricht ab | Pfad-Diskrepanz, Sync bricht ab | Ledger verfolgt Verschiebungen, gleicht Pfade ab |

Die letzte Zeile ist wichtiger als es scheint. Eine Seite in einer Web-Oberfläche umzubenennen oder zu verschieben, während jemand den alten Pfad in Git bearbeitet, ist einer der schwierigsten Grenzfälle. Die meisten Tools geben hier auf. Das Content Ledger verfolgt Verschiebungsoperationen explizit, sodass es weiß, dass `/docs/auth.md` zu `/docs/authentication.md` wurde, und die eingehende Git-Bearbeitung auf den korrekten neuen Pfad anwenden kann.

## Warum nicht einfach Git direkt verwenden?

Wenn Git so zentral für dieses Design ist, warum nicht den Web-Editor überspringen und Git direkt verwenden? Zwei Gründe:

Erstens, nicht jeder in einem Dokumentationsteam verwendet Git. Produktmanager, Support-Ingenieure und technische Redakteure bevorzugen oft einen Web-Editor. Sie in einen Git-Workflow zu zwingen, erzeugt Reibung und reduziert Beiträge.

Zweitens, Git allein gibt Ihnen keine veröffentlichte Dokumentation. Sie brauchen noch eine Rendering-Schicht, Suchindizierung, Zugriffskontrolle und eine Navigationsstruktur. Valoryx bietet all das und behält Git als kanonische Speicherschicht bei.

Das Content Ledger überbrückt diese beiden Welten. Git-Benutzer arbeiten in Git. Web-Benutzer arbeiten im Browser. Beide Workflows sind erstklassig, und das Ledger hält sie konsistent.

## Git-Sync einrichten

Wenn Sie das mit Ihrem eigenen Repository ausprobieren möchten:

1. [Valoryx installieren](/install/) — einzelnes Binary, keine externen Abhängigkeiten
2. Einen Workspace erstellen und ihn in den Workspace-Einstellungen mit einem Git-Repository verbinden
3. Die Remote-URL, den Branch und das Sync-Intervall konfigurieren
4. Von beiden Seiten bearbeiten

Der [Git-Integrationsleitfaden](/docs/guides/git-integration/) deckt die vollständige Einrichtung ab, einschließlich SSH-Schlüssel-Konfiguration, Branch-Strategien und Sync-Intervall-Optimierung.

Für Teams, die bereits Dokumentation in Git-Repositories verwalten, bedeutet das: Sie müssen sich nicht zwischen einem guten Bearbeitungserlebnis und einem Git-nativen Workflow entscheiden. Das Content Ledger macht beides möglich, ohne die Kompromisse, die jeden anderen Ansatz plagen, den wir getestet haben.
