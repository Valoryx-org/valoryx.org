---
title: "Selbstgehostete Dokumentation für regulierte Teams"
description: "Wenn Ihre Daten Ihre Infrastruktur nicht verlassen dürfen, schrumpfen die Dokumentationsoptionen. Worauf Sie achten sollten und wie selbstgehostete Tools Compliance-Anforderungen erfüllen."
date: "2026-03-23"
author: "Valoryx Team"
tags: ["compliance", "self-hosted", "security", "documentation"]
---

Wenn Sie im Gesundheitswesen, in der Verteidigung, im Finanzwesen oder in einer anderen Branche arbeiten, in der Datenresidenz wichtig ist, haben Sie das Gespräch bereits geführt: „Können wir dieses SaaS-Tool verwenden, oder muss es durch eine sechsmonatige Sicherheitsüberprüfung?" Bei den meisten Cloud-Dokumentationsplattformen ist die Antwort die Überprüfung — und sie endet oft mit „Nein."

Das Problem ist nicht, dass Cloud-Tools unsicher sind. Die meisten von ihnen sind in Sachen Sicherheit kompetent. Das Problem ist die Kontrolle. Regulierte Umgebungen müssen nachweisen, wo Daten liegen, wer Zugriff hat, wie sie verschlüsselt sind und was passiert, wenn etwas schiefgeht. Bei einer SaaS-Plattform vertrauen Sie deren Antworten. Bei selbstgehosteten Lösungen können Sie Ihre eigenen überprüfen.

## Warum Dokumentation bei der Compliance übersehen wird

Sicherheitsteams prüfen Datenbanken, Code-Repositories und Kommunikationstools. Dokumentationsplattformen rutschen oft durch, weil sie als „nur Docs" angesehen werden — interne Wikis mit Besprechungsnotizen und Onboarding-Leitfäden.

Aber Dokumentation enthält häufig:

- **Architekturdiagramme** mit Netzwerktopologie und IP-Bereichen
- **API-Spezifikationen** mit Authentifizierungsabläufen und Token-Formaten
- **Runbooks** mit Anmeldedaten, Connection Strings und Eskalationsverfahren
- **Kundenseitige Dokumentation** mit Produktfähigkeiten, die exportkontrolliert sind
- **Incident Reports** mit Details zu Sicherheitslücken

Das ist sensibles Material. Wenn es auf einem Drittanbieter-Server in einem Rechtsraum liegt, den Sie nicht kontrollieren, sind Sie möglicherweise ohne es zu wissen nicht compliant.

## Die Compliance-Checkliste

Bei der Bewertung von Dokumentationstools für regulierte Umgebungen sind dies die unverzichtbaren Anforderungen:

### Datenresidenz

Wo liegen die Daten physisch? Bei selbstgehosteten Tools ist die Antwort einfach: auf Ihrer Infrastruktur, in Ihrer gewählten Region. Bei SaaS-Tools müssen Sie die Rechenzentrumsstandorte des Anbieters und alle Drittanbieter-Unterauftragsverarbeiter überprüfen.

Unter der [DSGVO](https://commission.europa.eu/law/law-topic/data-protection_en) erfordern Übermittlungen personenbezogener Daten außerhalb der EU spezifische rechtliche Mechanismen. Wenn Ihre Dokumentation personenbezogene Daten enthält (Mitarbeiternamen, Kundeninformationen, Nutzerforschung), ist der Hosting-Standort relevant.

### Authentifizierung und Zugriffskontrolle

Wer kann auf die Dokumentation zugreifen und wie weisen Sie es nach? Regulierte Umgebungen erfordern typischerweise:

- **Multi-Faktor-Authentifizierung** — Passwörter allein reichen nicht aus
- **Rollenbasierte Zugriffskontrolle (RBAC)** — nicht jeder sollte alles sehen
- **Sitzungsverwaltung** — automatische Timeouts, Limits für gleichzeitige Sitzungen
- **Audit Trail** — wer hat wann von wo auf was zugegriffen

### Verschlüsselung

Daten müssen bei der Übertragung und im Ruhezustand verschlüsselt sein. „Wir verwenden HTTPS" deckt die Übertragung ab. Im Ruhezustand ist die schwierigere Frage: Ist die Datenbank verschlüsselt? Sind Dateianhänge verschlüsselt? Welcher Algorithmus und welche Schlüssellänge?

### Audit-Logging

Compliance-Frameworks erfordern Nachweise. Wenn ein Auditor fragt „Wer hat dieses Dokument am 15. März aufgerufen?", brauchen Sie eine Antwort. Audit-Logs müssen erfassen:

- Benutzeridentität (nicht nur „jemand")
- Durchgeführte Aktion (Lesen, Schreiben, Löschen, Export)
- Zeitstempel
- IP-Adresse oder Sitzungskennung
- Erfolg oder Fehlschlag

### Datenportabilität

Wenn Sie das Tool wechseln müssen — oder wenn ein Regulator einen Datenexport verlangt — können Sie Ihre Inhalte in einem Standardformat herausbekommen? Proprietäre Formate erzeugen Lock-in und Compliance-Risiko.

## Was Valoryx bietet

So adressiert Valoryx jede Anforderung. Das sind keine Marketing-Behauptungen — es sind Implementierungsdetails, die Sie in der [Sicherheitsdokumentation](/security/) und im Quellcode verifizieren können.

### Authentifizierung

Valoryx unterstützt WebAuthn/Passkey-Authentifizierung und traditionelle Passwort-Authentifizierung. Passwörter werden mit **Argon2id** gehasht — dem Gewinner des Password Hashing Competition, entwickelt um sowohl GPU- als auch ASIC-Angriffen zu widerstehen. Argon2id ist die aktuelle Empfehlung der OWASP für Passwortspeicherung.

RBAC ist mit fünf Rollen eingebaut: Owner, Admin, Editor, Viewer und Guest. Jede Rolle hat explizite Berechtigungen für Workspace-Zugriff, Seitenbearbeitung, Benutzerverwaltung und Systemkonfiguration. Berechtigungen werden auf API-Ebene durchgesetzt, nicht nur in der Oberfläche — selbst direkte API-Aufrufe respektieren Rollengrenzen.

### Verschlüsselung

Alle Daten im Ruhezustand werden mit **AES-256-GCM** verschlüsselt. Das umfasst die SQLite-Datenbank, Dateianhänge und jeden gecachten Inhalt. AES-256-GCM bietet sowohl Vertraulichkeit als auch Integrität — manipulierte Daten werden erkannt, nicht nur unlesbar.

Während der Übertragung liefert Valoryx über HTTPS. Bei Installationen hinter einem Reverse-Proxy (das übliche Muster) terminiert TLS am Proxy. Die [Installationsanleitung](/install/) behandelt sowohl direkte TLS- als auch Reverse-Proxy-Konfigurationen.

### Content Security Policy

Valoryx sendet strikte **Content Security Policy (CSP)**-Header, die Cross-Site-Scripting, Clickjacking und Datenexfiltration über Inline-Skripte verhindern. CSP-Header sind standardmäßig konfiguriert — keine manuelle Einrichtung erforderlich.

### Audit-Logging

Jede signifikante Aktion wird protokolliert: Seitenaufrufe, Bearbeitungen, Löschungen, Anmeldeversuche (erfolgreich und fehlgeschlagen), Berechtigungsänderungen, Git-Sync-Operationen und API-Schlüssel-Nutzung. Logs enthalten Benutzeridentität, Zeitstempel, IP-Adresse und die spezifisch betroffene Ressource.

Logs werden lokal in derselben SQLite-Datenbank gespeichert, was bedeutet, dass sie von denselben Verschlüsselungs- und Backup-Richtlinien wie Ihr Inhalt abgedeckt sind. Für Organisationen, die Logs an ein SIEM weiterleiten, ist das Aktivitätslog über die Admin-API zugänglich.

### Datenportabilität

Alle Inhalte werden als Standard-Markdown gespeichert. Git-Sync bedeutet, dass Ihre Inhalte bereits in einem Git-Repository in Klartextdateien existieren. Wenn Sie morgen aufhören, Valoryx zu verwenden, ist Ihre Dokumentation immer noch da — in Ihrem Repository, in Standardformat, mit vollständiger Historie.

Kein proprietärer Exportschritt. Kein „Als ZIP herunterladen"-Workaround. Ihre Inhalte sind immer in dem Format zugänglich, in dem Sie sie geschrieben haben.

## Vergleich: Selbstgehostet vs. Cloud für Compliance

| Anforderung | Cloud SaaS | Selbstgehostet (Valoryx) |
|-------------|------------|--------------------------|
| Datenresidenz | Rechenzentren des Anbieters (Regionen überprüfen) | Ihre Infrastruktur, Ihre Region |
| Authentifizierung | Vom Anbieter verwaltet (meist OAuth/SAML) | Sie kontrollieren: WebAuthn, Argon2id-Passwörter, RBAC |
| Verschlüsselung im Ruhezustand | Vom Anbieter verwaltet (Algorithmus überprüfen) | AES-256-GCM, Schlüssel auf Ihrem Server |
| Audit-Logs | Log-Format des Anbieters, deren Aufbewahrung | Ihre Logs, Ihre Aufbewahrung, Ihr SIEM |
| Unterauftragsverarbeiter | Lieferantenkette des Anbieters (DPA lesen) | Keine — einzelnes Binary, keine externen Aufrufe |
| Datenexport | Exportformat des Anbieters (möglicherweise proprietär) | Standard-Markdown in einem Git-Repository |
| Incident Response | Anbieter benachrichtigt Sie (SLA-Timing prüfen) | Sie erkennen, Sie reagieren, Sie kontrollieren den Zeitrahmen |

Die Zeile „Unterauftragsverarbeiter" verdient Betonung. Viele SaaS-Dokumentationstools verwenden Drittanbieterdienste für Suche (Algolia), Analytics (Segment), Fehlertracking (Sentry) und Hosting (AWS, GCP). Jeder Unterauftragsverarbeiter ist ein Glied in der Compliance-Kette, das seine eigene Bewertung braucht. Valoryx ist ein einzelnes Go-Binary ohne externe Abhängigkeiten und ohne ausgehende Netzwerkaufrufe. Es gibt keine Lieferantenkette zu prüfen.

## Praktische Schritte

Wenn Sie Dokumentationstools für eine regulierte Umgebung bewerten:

1. **Kartieren Sie Ihre Daten.** Was steht tatsächlich in Ihrer Dokumentation? Architekturdetails, Anmeldedaten, Kundendaten? Das bestimmt, welche Compliance-Frameworks gelten.

2. **Prüfen Sie die Anforderungen Ihres Frameworks.** DSGVO, SOC 2, HIPAA, ITAR und FedRAMP haben jeweils unterschiedliche Anforderungen an Datenresidenz, Verschlüsselung und Zugriffskontrolle. Wissen Sie, welche für Ihre Organisation gelten.

3. **Probieren Sie zunächst selbstgehostet.** [Installieren Sie Valoryx](/install/) auf Ihrer Infrastruktur, verbinden Sie es mit Ihrem Identity Provider und überprüfen Sie die Sicherheitskontrollen selbst. Die Community Edition ist kostenlos ohne Funktionseinschränkungen — dieselbe Authentifizierung, Verschlüsselung und Audit-Logging in jeder Installation.

4. **Dokumentieren Sie Ihre Kontrollen.** Wenn der Auditor kommt, müssen Sie zeigen: wo Daten liegen, wie sie verschlüsselt sind, wer Zugriff hat und was der Audit Trail zeigt. Selbstgehostete Tools machen jede dieser Fragen mit Nachweisen aus Ihren eigenen Systemen beantwortbar.

Lesen Sie unsere [Datenschutzrichtlinie](/privacy/) und [Nutzungsbedingungen](/terms/) für Details darüber, wie Valoryx Daten in unserem Cloud-Angebot handhabt. Bei selbstgehosteten Installationen berühren Ihre Daten nie unsere Infrastruktur.

Compliance sollte Ihre Werkzeugwahl nicht diktieren — tut es aber oft. Selbstgehostete Dokumentation gibt regulierten Teams eine Sache weniger, die sie dem Auditor erklären müssen, und ein weiteres System vollständig unter ihrer eigenen Kontrolle.
