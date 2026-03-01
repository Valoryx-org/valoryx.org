---
title: "Warum jedes git-Docs-Tool die Synchronisation kaputtmacht (und wie wir es gelöst haben)"
description: "Jede Dokumentationsplattform behauptet, git-Integration zu haben. Die meisten lügen. Hier ist, was wirklich schiefläuft — und das Content-Ledger-Muster, das das Problem endlich löst."
date: "2026-02-22"
author: "Valoryx Team"
tags: ["git-sync", "Dokumentation", "Architektur"]
---

Wenn man technische Dokumentation pflegt, wurde man wahrscheinlich schon einmal von "Vollständiger git-Integration" enttäuscht. Man verbindet das Repository, pusht einen Commit aus der IDE — und alles bricht zusammen. Merge-Konflikte. Verlorene Bearbeitungen. Seiten, die stillschweigend zurückgesetzt werden.

Das ist kein Bug. Es ist ein grundlegender Designfehler.

## Die drei Arten, wie git-Sync scheitert

### 1. Einseitiger Spiegel, kein echter Sync

Die meisten Plattformen behandeln git als Backup-Ziel. Bearbeitungen fließen von der Web-UI in git, aber Änderungen, die aus einer IDE gepusht werden, werden ignoriert oder verursachen Konflikte. GitBooks "Git Sync" ist das bekannteste Beispiel.

### 2. Datenbank zuerst, git zweitrangig

Wiki.js speichert Inhalte in einer Datenbank. git-Sync ist optional, aber die Datenbank ist immer kanonisch. Man kann nicht `git clone` ausführen, Änderungen pushen und sie in der UI sehen, ohne zuerst durch die Datenbank zu gehen.

### 3. Destruktive Konfliktlösung

Wenn der Sync abbricht, gehen die meisten Plattformen damit schlecht um — sie überschreiben stillschweigend eine Version, erstellen doppelte Seiten oder markieren den Sync einfach als "fehlgeschlagen".

## Warum das schwierig ist

Bidirektionaler Sync ist schwierig, weil Web-UIs sofortige atomare Schreibvorgänge erwarten, während git auf Snapshots basiert. Eine zeitliche Lücke erzeugt Divergenz.

Ein Beispiel: Alice bearbeitet eine Datei im Web-Editor. Bob bearbeitet dieselbe Datei in VS Code und pusht. Alice speichert. Jetzt existieren zwei divergierende Commits auf demselben Branch.

## Das Content-Ledger-Muster

Valoryx' Lösung: Jede Mutation ist ein Ereignis in einem append-only, total geordneten Ledger.

**Jede Mutation ist ein Ereignis.** Der Web-Editor erstellt einen Ledger-Eintrag ("Seite X geändert, hier ist das Diff"), anstatt direkt in git oder die Datenbank zu schreiben.

**Ereignisse werden auf beide Ziele angewendet.** Ein Worker wendet jedes Ledger-Ereignis sowohl auf die Datenbank als auch auf das git-Repository an. Beide konvergieren zum gleichen Zustand.

**git-Pushes werden zu Ledger-Einträgen.** Ein Webhook wandelt eingehende Commits in Ledger-Einträge um. Die Web-UI aktualisiert sich innerhalb von Sekunden.

**Konflikte sind konzeptbedingt unmöglich.** Da alle Mutationen durch den Ledger serialisiert werden, können zwei Schreibvorgänge niemals divergieren.

## Was das in der Praxis bedeutet

- Im Browser bearbeiten → Commit erscheint in `git log` innerhalb von Sekunden
- Aus VS Code pushen → Änderung erscheint in der Web-UI ohne manuellen Sync
- CI-Pipelines modifizieren Docs → Ergebnisse erscheinen im Web-Editor
- Beliebige Änderung mit `git revert` rückgängig machen → Web-UI spiegelt es sofort wider

Kein Sync-Status zu prüfen. Keine Konfliktlösungs-UI. Keine Divergenz.

## Selbst ausprobieren

Valoryx ist eine einzelne Go-Binary. Herunterladen, auf ein git-Repository zeigen und bidirektionalen Sync erleben, der wirklich funktioniert.
