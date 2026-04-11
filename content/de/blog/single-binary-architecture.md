---
title: "Warum wir ein einzelnes Go-Binary ausliefern"
description: "DocPlatform ist ein Binary ohne Abhängigkeiten. Kein Docker, kein Postgres, kein Redis. Die Architektur hinter einer 30-Sekunden-Installation."
date: "2026-03-30"
author: "Valoryx Team"
tags: ["architecture", "golang", "self-hosted", "documentation"]
---

Die meisten Dokumentationsplattformen werden als Stack ausgeliefert. Sie bekommen eine Node.js-Anwendung, eine PostgreSQL-Datenbank, einen Redis-Cache, einen Elasticsearch-Cluster für die Suche und einen Nginx-Reverse-Proxy, der alles zusammenhält. Fünf Dienste, fünf Dinge, die kaputtgehen können, fünf Dinge, die überwacht, gepatcht und aktualisiert werden müssen.

DocPlatform wird als eine Datei ausgeliefert. Herunterladen, ausführen, fertig.

Das ist kein Marketing-Trick. Es ist eine Architekturentscheidung, die wir am ersten Tag getroffen haben, und jede Designentscheidung seitdem folgt daraus. Hier ist der Grund.

## Der typische Dokumentations-Stack

Schauen wir uns an, was Sie tatsächlich deployen, wenn Sie eine moderne Dokumentationsplattform einrichten:

```
┌─────────────┐
│   Nginx     │  ← Reverse-Proxy, TLS-Terminierung
├─────────────┤
│   Node.js   │  ← Applikationsserver
├─────────────┤
│  PostgreSQL │  ← Inhaltsspeicherung
├─────────────┤
│    Redis    │  ← Session-Cache, Job-Queue
├─────────────┤
│Elasticsearch│  ← Volltextsuche
└─────────────┘
```

Das sind fünf Prozesse, jeder mit eigenen Konfigurationsdateien, Versionsanforderungen und Fehlermodi. Docker Compose hilft bei der Orchestrierung, reduziert aber nicht die Angriffsfläche. Sie müssen weiterhin:

- Jeden Dienst auf Abstürze und Ressourcenverbrauch überwachen
- Datenbankmigrationen bei Upgrades ausführen
- Elasticsearch-Heap-Größen und Index-Einstellungen tunen
- Redis-Eviction-Policies handhaben, wenn der Speicher voll wird
- Nginx-Logs rotieren und TLS-Zertifikate erneuern

Für ein Fortune-500-Unternehmen mit einem Plattformteam ist das Routine. Für ein 10-Personen-Startup, das einfach interne Dokumentation will, ist es nie endender Overhead.

## Was ein einzelnes Binary aussieht

Hier ist das DocPlatform-Deployment:

```
┌──────────────────────────┐
│      docplatform          │  ← einzelnes Go-Binary
│  ┌────────┐ ┌──────────┐ │
│  │ SQLite │ │  Bleve   │ │
│  │  (DB)  │ │ (Suche)  │ │
│  └────────┘ └──────────┘ │
└──────────────────────────┘
```

Ein Binary. Ein Datenverzeichnis. SQLite übernimmt Inhaltsspeicherung, Sitzungen und Konfiguration. [Bleve](https://blevesearch.com/) übernimmt die Volltextsuche. Beides sind eingebettete Bibliotheken, die direkt in das Binary kompiliert werden — keine externen Prozesse, keine Netzwerkaufrufe zwischen Diensten.

Die Installation dauert 30 Sekunden:

```bash
curl -fsSL https://get.valoryx.org | sh
docplatform serve
```

Das war's. Kein `docker-compose up`, keine Datenbankinitialisierung, keine Umgebungsvariablen für Connection Strings. Das Binary erstellt sein Datenverzeichnis beim ersten Start und beginnt auf Port 3000 zu liefern.

Weitere Installationsoptionen finden Sie in der [Installationsanleitung](/install/).

## Warum Go das ermöglicht

Wir haben Go speziell gewählt, weil es diese Architektur ermöglicht. Drei Eigenschaften sind entscheidend:

### Statische Kompilierung

Go kompiliert zu einem einzelnen statisch gelinkten Binary. Keine Laufzeitabhängigkeiten, keine Shared Libraries, keine JVM, kein `node_modules`. Das Binary läuft auf einem nackten Linux-Server, auf dem nichts anderes installiert ist.

```bash
# Cross-Kompilierung für Linux von jedem OS
GOOS=linux GOARCH=amd64 go build -o docplatform ./cmd/server/
```

Dieser eine Befehl produziert ein Binary, das Sie per `scp` auf einen Server kopieren und ausführen können. Vergleichen Sie das mit dem Deployment einer Node.js-Anwendung, wo Sie Node installieren, `npm install` ausführen, hoffen müssen, dass die nativen Abhängigkeiten auf der Zielarchitektur korrekt kompilieren, und einen Prozessmanager konfigurieren.

### Goroutines für Nebenläufigkeit

Eine Dokumentationsplattform muss gleichzeitige Anfragen verarbeiten (Seitenaufrufe, Suchabfragen, Editor-Speichervorgänge), Hintergrundjobs ausführen (Git-Sync, Suchindizierung) und WebSocket-Verbindungen verwalten (Echtzeit-Zusammenarbeit) — alles gleichzeitig.

Gos Goroutines machen das günstig. Jede WebSocket-Verbindung bekommt ihre eigene Goroutine, die etwa 2 KB Speicher kostet. Ein Node.js-Server, der dieselben Verbindungen verarbeitet, muss sie auf einer einzigen Event-Loop verwalten oder an Worker-Threads mit Shared-Memory-Komplexität delegieren.

Die Git-Sync-Engine, die Änderungen zwischen dem Web-Editor und Git-Repositories abfragt und abgleicht, läuft als eine Reihe von Goroutines innerhalb desselben Prozesses. Kein separater Worker-Dienst, keine Job-Queue, kein Redis.

### Eingebettete Datenbanken

Sowohl SQLite als auch Bleve sind in C beziehungsweise Go geschrieben und kompilieren beide direkt in das Binary über `cgo` (SQLite) und reines Go (Bleve). Das bedeutet:

- Kein Datenbankserver zu installieren, konfigurieren oder überwachen
- Keine Netzwerklatenz zwischen der Anwendung und ihren Daten
- Backups sind Dateikopien — `cp data.db data.db.bak`
- Upgrades bewahren Daten automatisch — das neue Binary liest die alten Datendateien

SQLite verarbeitet [Milliarden von Zeilen](https://www.sqlite.org/whentouse.html) in der Produktion bei Unternehmen, die weit größer sind als unseres. Für eine Dokumentationsplattform, die Hunderte gleichzeitiger Benutzer bedient, ist es mehr als ausreichend.

## Der operationelle Vorteil

Der Single-Binary-Ansatz zahlt sich im Betrieb aus:

**Upgrades** bedeuten, eine Datei zu ersetzen. Das alte Binary stoppen, das neue kopieren, starten. Keine Datenbankmigrationen — die Anwendung verarbeitet Schemaänderungen beim Start.

**Backups** bedeuten, zwei Dateien zu kopieren: die SQLite-Datenbank und den Bleve-Index. Oder nur die Datenbank — der Suchindex kann aus dem Inhalt neu aufgebaut werden.

**Monitoring** bedeutet, einen Prozess zu beobachten. Wenn er läuft, läuft alles. Wenn er abstürzt, neu starten. Es gibt keinen teilweisen Ausfall, bei dem die Datenbank läuft, aber die Suche ausgefallen ist.

**Ressourcenverbrauch** ist vorhersehbar. Ein Prozess, ein Speicherbedarf. Keine überraschenden Speicherspitzen vom JVM-Heap von Elasticsearch oder Redis, das Schlüssel anhäuft.

**Sicherheitsoberfläche** ist minimal. Ein Binary, ein lauschender Port. Keine Inter-Service-Kommunikation abzusichern, kein Redis auf einem Netzwerkport exponiert, kein Elasticsearch-Cluster mit eigener Authentifizierungsschicht. Siehe unsere [Sicherheitsdokumentation](/security/) für das vollständige Modell.

## Kompromisse, die wir akzeptieren

Diese Architektur hat Grenzen, und wir sind ehrlich darüber:

**Nur vertikale Skalierung.** SQLite läuft auf einer Maschine. Sie können die Datenbank nicht über einen Cluster verteilen. Für die meisten Dokumentationsanwendungsfälle — selbst große mit Tausenden von Seiten — bewältigt ein einzelner moderner Server die Last problemlos. Aber wenn Sie horizontale Skalierung über Rechenzentren hinweg brauchen, ist dies nicht die richtige Architektur.

**Single-Writer für SQLite.** SQLite unterstützt gleichzeitige Leser, serialisiert aber Schreibvorgänge. In der Praxis sind Dokumentationsplattformen leselastig (viele Seitenaufrufe, wenige Bearbeitungen), sodass dies selten ein Engpass ist. Aber ein Team von 200 Personen, die alle gleichzeitig Seiten speichern, würde etwas Schreibkontention erleben.

**Kein Komponentenaustausch.** Sie können Bleve nicht durch Elasticsearch ersetzen, wenn Sie erweiterte Suchfunktionen wollen. Die Suchmaschine ist eingebettet, nicht austauschbar. Wir denken, der Kompromiss lohnt sich — Bleve unterstützt Stemming, Fuzzy-Matching und Field-Boosting, was die Anforderungen der Dokumentationssuche abdeckt.

## Deployment-Beispiele

Das einzelne Binary läuft überall, wo ein Linux/macOS/Windows-Prozess laufen kann:

**Bare Metal oder VM:**
```bash
# Herunterladen, ausführen, fertig
curl -fsSL https://get.valoryx.org | sh
docplatform serve --port 3000
```

**Systemd-Dienst:**
```ini
[Unit]
Description=DocPlatform
After=network.target

[Service]
ExecStart=/opt/docplatform/bin/docplatform serve
WorkingDirectory=/opt/docplatform
Restart=always

[Install]
WantedBy=multi-user.target
```

**Docker (falls gewünscht):**
```dockerfile
FROM scratch
COPY docplatform /docplatform
ENTRYPOINT ["/docplatform", "serve"]
```

Beachten Sie `FROM scratch` — da das Binary keine Abhängigkeiten hat, enthält das Docker-Image buchstäblich nichts außer dem Binary selbst. Das Image ist unter 30 MB groß.

Detaillierte Deployment-Optionen finden Sie im [Binary-Deployment-Leitfaden](/docs/deployment/binary/).

## Was das für Ihr Team bedeutet

Jeder zusätzliche Dienst in Ihrem Stack ist ein Dienst, den jemand verstehen, überwachen und um 2 Uhr morgens reparieren muss, wenn er ausfällt. Dokumentationsinfrastruktur sollte in den Hintergrund treten — sie sollte etwas sein, das Sie einmal einrichten und dann vergessen.

Ein einzelnes Binary, das alles einbettet, was es braucht, kommt diesem Ideal am nächsten. Keine Container zu orchestrieren, keine Datenbanken zu tunen, keine Such-Cluster zu überwachen. Nur eine Datei, die Ihre Dokumentation betreibt.

[Installieren Sie DocPlatform](/install/) in 30 Sekunden und überzeugen Sie sich selbst. Die Community Edition ist kostenlos — unbegrenzte Benutzer, unbegrenzte Seiten, keine Zeitbegrenzung.
