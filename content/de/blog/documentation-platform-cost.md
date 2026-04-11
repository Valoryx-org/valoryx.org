---
title: "Die wahren Kosten von Dokumentationsplattformen"
description: "Pro-Benutzer-Preise bestrafen die Dokumentationsadoption. Hier ist ein TCO-Vergleich bei 5, 15, 50 und 100 Benutzern — mit tatsächlichen Zahlen."
date: "2026-04-09"
author: "Valoryx Team"
tags: ["pricing", "comparison", "documentation"]
---

Pro-Benutzer-Preise klingen auf den ersten Blick vernünftig. Fünf Benutzer für 8 $/Monat? Das sind 40 $. Ihr Team kann sich 40 $ leisten.

Aber Dokumentation ist eines dieser Tools, bei dem die Anzahl der Personen, die Zugang haben *sollten*, ständig wächst. Ingenieure müssen schreiben. Produktmanager müssen reviewen. Support-Mitarbeiter müssen nachschlagen. Neue Mitarbeiter müssen lesen und kommentieren. Plötzlich sind Sie nicht bei 5 Plätzen — Sie sind bei 50, und diese „erschwinglichen" 8 $/Platz sind 400 $/Monat für ein Tool, das Textdateien speichert.

Pro-Benutzer-Preise für Dokumentation haben einen perversen Anreiz: Sie bestrafen Unternehmen dafür, dass mehr Menschen zur Dokumentation beitragen. Manager beginnen, den Zugang einzuschränken. Leute teilen Passwörter. Dokumentation wird das Problem eines anderen. Und dann wundert man sich, warum die Dokumentation immer veraltet ist.

## Die Zahlen

Vergleichen wir die tatsächlichen monatlichen Kosten von vier Dokumentationsplattformen bei verschiedenen Teamgrößen. Dies sind Listenpreise von Anfang 2026.

| Benutzer | [GitBook](https://www.gitbook.com/pricing) (8 $/Benutzer) | Notion (10 $/Benutzer) | Confluence (6 $/Benutzer) | Valoryx Cloud | Valoryx CE |
|------:|------:|------:|------:|------:|------:|
| 5 | 40 $ | 50 $ | 30 $ | 29 $ | 0 $ |
| 15 | 120 $ | 150 $ | 90 $ | 29 $ | 0 $ |
| 50 | 400 $ | 500 $ | 300 $ | 29 $ | 0 $ |
| 100 | 800 $ | 1.000 $ | 600 $ | 29 $ | 0 $ |

Einige Anmerkungen zu diesen Zahlen:

**GitBook** berechnet 8 $/Benutzer/Monat im Plus-Plan. Das Free Tier ist auf 1 Space mit Grundfunktionen beschränkt. Veröffentlichte Dokumentation ist nur in kostenpflichtigen Plänen verfügbar.

**Notion** berechnet 10 $/Benutzer/Monat für den Plus-Plan. Notion ist ein allgemeines Workspace-Tool, keine Dokumentationsplattform — es fehlen veröffentlichte Docs, Git-Sync und zweckgebundene Dokumentationsfunktionen. Aber viele Teams nutzen es für Dokumentation, daher ist es ein fairer Preisvergleich.

**Confluence** berechnet 6,05 $/Benutzer/Monat (Standard) für Cloud. Das ist die aktuelle Atlassian-Preisgestaltung für 1–100 Benutzer. Die Data-Center-Version (selbstgehostet) beginnt bei 27.000 $/Jahr für 500 Benutzer.

**Valoryx Cloud** kostet pauschal 29 $/Monat für den Team-Plan — 3 Workspaces, 15 Editoren, 150 Seiten. Nicht pro Platz. Der [Free-Plan](/pricing/) gibt Ihnen 1 Workspace, 3 Editoren, 50 Seiten für 0 $.

**Valoryx Community Edition** kostet 0 $. Für immer. Unbegrenzt alles. Sie hosten es selbst.

## Das Skalierungsproblem

Schauen Sie sich die 5-Benutzer-Spalte an. Jede Plattform ist erschwinglich. GitBook für 40 $/Monat ist weniger als ein Team-Mittagessen. Niemand wird über 40 $ streiten.

Schauen Sie sich jetzt die 100-Benutzer-Spalte an. GitBook kostet 800 $/Monat — 9.600 $/Jahr für ein Tool, das Markdown speichert und rendert. An diesem Punkt befinden Sie sich in einer Budget-Überprüfung, jemand fragt „Brauchen wir das wirklich?", und die Antwort lautet normalerweise „Beschränken wir den Zugang auf Leute, die tatsächlich Dokumentation schreiben."

Diese Entscheidung — den Zugang zu beschränken — ist der Punkt, an dem die Dokumentationsqualität stirbt.

Gute Dokumentation entsteht, wenn jeder beitragen kann. Der Ingenieur, der gerade ein Deployment-Problem debuggt hat, sollte den Deployment-Leitfaden aktualisieren können. Der Support-Mitarbeiter, der einen Workaround gefunden hat, sollte ihn zur Fehlerbehebungsseite hinzufügen können. Der neue Mitarbeiter, der mit dem Onboarding kämpfte, sollte die Onboarding-Dokumentation verbessern können.

Pro-Benutzer-Preise machen jeden dieser Beiträge 6–10 $/Monat teurer. Also bekommt man stattdessen: „Schreiben Sie eine E-Mail an das Docs-Team und bitten Sie sie, es zu aktualisieren." Das Docs-Team hat ein Backlog. Die Aktualisierung passiert nie. Das Wissen bleibt im Kopf von jemandem, bis er das Unternehmen verlässt.

## Gesamtbetriebskosten

Der monatliche Abonnementpreis ist nur ein Teil der Kosten. Die tatsächlichen TCO umfassen:

### Infrastrukturkosten (nur bei Selbsthosting)

Wenn Sie die Valoryx Community Edition wählen, brauchen Sie einen Server. Ein Hetzner CX22 (2 vCPU, 4 GB RAM) kostet 3,99 EUR/Monat. DocPlatform verbraucht unter normaler Last etwa 100 MB RAM. Dieser Server kann auch andere Dinge ausführen.

Jährliche Infrastrukturkosten für Selbsthosting: **ca. 50 $/Jahr.**

### Admin-Aufwand

**SaaS-Plattformen** erfordern fast keinen Admin-Aufwand für die Grundnutzung, verschlingen aber Stunden bei der SSO-Konfiguration, Benutzerbereitstellung/-deaktivierung und dem Kampf mit Berechtigungsmodellen, die nicht zu Ihrer Organisationsstruktur passen.

**Selbstgehostetes DocPlatform** erfordert die Ersteinrichtung (30 Minuten), gelegentliche Updates (neues Binary herunterladen, neu starten — 5 Minuten) und Backup-Verifizierung (automatisiert, aber monatliche Prüfung lohnt sich).

### Migrationskosten

Die versteckten Kosten jeder Plattform sind das, was passiert, wenn Sie wechseln möchten. Der Export von Confluence ist berüchtigt schmerzhaft — Jahre von Inhalten in einem proprietären Speicherformat eingesperrt. GitBook exportiert nach Markdown, verliert aber Metadaten.

DocPlatform speichert alles als Markdown in einem Git-Repository. Ihre Inhalte sind immer außerhalb der Plattform zugänglich, in einem Standardformat, mit vollständiger Versionshistorie. Die Migrationskosten sind null, weil es nichts zu migrieren gibt — Ihre Inhalte leben bereits in Git.

## Das Argument für Pauschalpreise

Valoryx Cloud verwendet Pauschalpreise statt Pro-Platz:

| Plan | Preis | Workspaces | Editoren | Seiten |
|------|------:|------:|------:|------:|
| Free | 0 $/Monat | 1 | 3 | 50 |
| Team | 29 $/Monat | 3 | 15 | 150 |
| Business | Demnächst | Mehr | Mehr | Mehr |

Die Limits gelten für Workspaces und Seiten, nicht für Benutzer. Der Team-Plan für 29 $/Monat unterstützt 15 Editoren — bei jeder Pro-Platz-Plattform würden 15 Benutzer 90–150 $/Monat kosten.

Noch wichtiger: Leser sind kostenlos. Wenn Ihr Unternehmen 200 Personen hat, die Dokumentation lesen müssen, aber nur 15, die schreiben, zahlen Sie nicht für 200 Plätze. Sie zahlen für den Team-Plan.

Das richtet die Anreize korrekt aus: Sie wollen, dass so viele Menschen wie möglich Ihre Dokumentation lesen und dazu beitragen. Das Preismodell sollte das nicht bestrafen.

## Wann Pro-Platz sinnvoll ist

Pro-Platz-Preise sind nicht immer falsch. Für Tools, bei denen jeder Benutzer signifikante Kosten verursacht (rechenintensive Workloads, speicherintensive Anwendungen), spiegelt die Berechnung pro Benutzer den tatsächlichen Ressourcenverbrauch wider.

Dokumentationsplattformen haben diese Eigenschaft nicht. Markdown zu rendern ist günstig. Text zu speichern ist günstig. Die Grenzkosten für das Hinzufügen des 51. Benutzers zu einer Dokumentationsplattform sind annähernd null. 6–10 $/Monat für diesen 51. Benutzer zu berechnen, ist eine Geschäftsmodellentscheidung, keine kostenreflektierende.

## Die Community-Edition-Kalkulation

Für Teams, die selbst hosten können, ändert die Community Edition die Kalkulation grundlegend:

| Ausgabe | Jährliche Kosten |
|---|---:|
| Server (Hetzner CX22) | 50 $ |
| Domain | 12 $ |
| TLS-Zertifikat (Let's Encrypt) | 0 $ |
| DocPlatform CE Lizenz | 0 $ |
| **Gesamt** | **62 $/Jahr** |

Das sind 62 $/Jahr für unbegrenzte Benutzer, unbegrenzte Seiten, unbegrenzte Workspaces, Volltextsuche, Git-Sync, RBAC, WebAuthn und MCP-Integration. Keine Pro-Platz-Gebühren, keine Feature-Einschränkungen, kein „Kontaktieren Sie den Vertrieb für Enterprise-Preise."

Bei 100 Benutzern sind das 0,62 $/Benutzer/Jahr gegenüber 72–120 $/Benutzer/Jahr bei gehosteten Pro-Platz-Plattformen.

## Die Entscheidung treffen

Hier ist ein einfaches Framework:

**Wählen Sie Valoryx Cloud (29 $/Monat)**, wenn Sie keine Infrastruktur verwalten möchten, aber Pauschalpreise wollen. Gut für kleine bis mittlere Teams, die eine gehostete Lösung ohne Pro-Platz-Kostenskalierung wollen.

**Wählen Sie Valoryx Community Edition (0 $)**, wenn Ihr Team einen Linux-Server verwalten kann. Am besten für Teams, die Wert auf Datensouveränität legen, keine wiederkehrenden Kosten wollen oder Compliance-Anforderungen haben, die Selbsthosting verlangen. Siehe die [Installationsanleitung](/install/).

**Wählen Sie eine Pro-Platz-Plattform**, wenn Ihre Organisation weniger als 10 Benutzer hat, Ihr Team nicht viel Dokumentation schreibt und Sie bereits im Ökosystem des Anbieters verankert sind (z. B. Confluence, wenn Sie voll auf Atlassian setzen).

**Entscheiden Sie nicht auf Basis des 5-Benutzer-Preises.** Entscheiden Sie auf Basis des 50-Benutzer-Preises, denn dorthin geht die Reise. Dokumentationstools haben die Tendenz, sich über Organisationen auszubreiten — wenn das Tool gut ist, wollen mehr Leute Zugang. Ihr Preismodell sollte das belohnen, nicht bestrafen.

Vergleichen Sie alle Pläne auf der [Preisseite](/pricing/) oder sehen Sie sich die [Open-Source-Seite](/open-source/) für die vollständige Feature-Liste der Community Edition an.
