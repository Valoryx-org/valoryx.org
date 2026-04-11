---
title: "Ihre Dokumentation gehört in Git. Punkt."
description: "Code lebt in Git. Infrastruktur lebt in Git. Warum lebt Ihre Dokumentation immer noch in einem Wiki? Ein Argument für versionskontrollierte Dokumentation."
date: "2026-03-09"
author: "Valoryx Team"
tags: ["git", "documentation", "opinion"]
---

Hier ist eine Bestandsaufnahme dessen, was ein typisches Engineering-Team in Git aufbewahrt:

- Anwendungsquellcode
- Infrastrukturdefinitionen (Terraform, Pulumi, CloudFormation)
- CI/CD-Pipeline-Konfigurationen
- Datenbankmigrationen
- API-Spezifikationen (OpenAPI, Protobuf)
- Deployment-Manifeste (Kubernetes, Docker Compose)
- Umgebungskonfigurations-Templates

Und hier ist, was normalerweise außerhalb von Git lebt:

- Dokumentation

Das ist merkwürdig. Dokumentation beschreibt das System. Sie ändert sich, wenn sich das System ändert. Sie braucht Review, Versionierung, Zuordnung und die Möglichkeit zum Rollback. Jedes andere Artefakt, das diese Eigenschaften teilt, lebt in Git. Dokumentation nicht — und niemand kann einen guten Grund dafür nennen.

## Die üblichen Ausreden

### „Nicht-technische Leute müssen Dokumentation bearbeiten"

Das ist das häufigste Argument dafür, Dokumentation in Confluence oder Notion zu halten. Und es ist berechtigt — Sie können einen Produktmanager nicht bitten, Git-Branching zu lernen, um einen Tippfehler zu korrigieren. Aber es ist kein Argument gegen Git. Es ist ein Argument für bessere Werkzeuge auf Git-Basis.

Git ist ein Speicher- und Versionierungs-Backend. Nichts erfordert, dass Menschen direkt damit interagieren. Ein Web-Editor kann Commits erstellen und Änderungen pushen, genauso wie eine CI-Pipeline. Der Benutzer schreibt im Browser; das System übernimmt die Git-Operationen.

Die Darstellung „Git vs. nicht-technische Benutzer" ist eine falsche Dichotomie. Sie können beides haben.

### „Dokumentation ändert sich zu oft für PRs"

Manche Teams haben das Gefühl, dass Pull Requests für Dokumentation das Schreiben verlangsamen würden. Und wenn Ihr PR-Prozess zwei Reviewer, einen CI-Check und eine Merge-Queue erfordert — ja, das ist zu viel Reibung für das Beheben eines Tippfehlers.

Aber nichts an Git schreibt einen schweren Review-Prozess vor. Sie können für kleinere Änderungen direkt auf main pushen und Branches für strukturelle Überarbeitungen verwenden. Der Punkt ist, dass die Historie existiert. Jede Änderung wird nachverfolgt, zugeordnet und ist rückgängig machbar. Ob Sie jede Änderung überprüfen, ist eine Prozessentscheidung, keine Werkzeugbeschränkung.

### „Unsere Dokumentationsplattform unterstützt kein Git"

Das war einmal richtig und es war einmal relevant. Confluence, Notion und die meisten Wikis speichern Inhalte in einer proprietären Datenbank ohne echte Git-Integration. Der Export nach Markdown ist verlustbehaftet und nur in eine Richtung möglich.

Aber das ist eine Einschränkung bestimmter Produkte, keine grundsätzliche Beschränkung. Dokumentationsplattformen, die Git als Source of Truth behandeln — und gleichzeitig einen Web-Editor zur Vereinfachung bieten — gibt es jetzt. Die Technologie hat den Bedarf eingeholt.

### „Markdown ist einschränkend"

Berechtigte Kritik für bestimmte Inhaltstypen. Markdown unterstützt nativ keine komplexen Tabellen, eingebetteten Diagramme oder interaktiven Elemente. Aber für 90 % der internen Dokumentation — Anleitungen, Runbooks, Architekturentscheidungen, API-Dokumentation, Onboarding-Materialien — ist Markdown mehr als ausreichend.

Und Markdown in Git gibt Ihnen etwas, das kein proprietäres Format bieten kann: Portabilität. Wenn Sie in zwei Jahren das Tool wechseln möchten, sind Ihre Inhalte Klartextdateien in einem Standardformat. Versuchen Sie einmal, fünf Jahre Confluence-Inhalte in etwas Brauchbares zu exportieren.

## Was Sie ohne Git verlieren

Wenn Ihre Dokumentation außerhalb von Git lebt, verlieren Sie Fähigkeiten, die Ingenieure bei Code als selbstverständlich betrachten:

### Blame

Wer hat diesen Absatz geschrieben, der behauptet, die API unterstütze Paginierung? Wann? Als Reaktion worauf? Mit `git blame` können Sie jede Zeile zu ihrem Autor, Zeitstempel und Commit-Nachricht zurückverfolgen. In einem Wiki bekommen Sie vielleicht „zuletzt bearbeitet von Sarah, vor 6 Monaten" — ohne Kontext dafür, warum.

### Branching

Sie schreiben den Deployment-Leitfaden für eine neue Infrastruktur um. Der alte Leitfaden muss genau bleiben, bis die Migration abgeschlossen ist. In Git erstellen Sie einen Branch. Beide Versionen existieren nebeneinander. Sie mergen, wenn die Migration abgeschlossen ist. In einem Wiki pflegen Sie entweder zwei Seiten (die zwangsläufig auseinanderdriften) oder bearbeiten vor Ort und hoffen, dass niemand den halb aktualisierten Anweisungen folgt.

### Atomare repository-übergreifende Änderungen

Die besten Dokumentationsänderungen passieren neben Codeänderungen. Ein PR, der einen API-Endpoint hinzufügt, sollte die Dokumentation für diesen Endpoint enthalten. Ein Commit, der ein Feature als veraltet markiert, sollte die Dokumentation im selben Commit aktualisieren — oder zumindest im selben PR. Wenn Dokumentation in einem Wiki lebt, ist diese Kopplung unmöglich. Der Code wird ausgeliefert, und jemand erstellt ein Ticket, „die Dokumentation zu aktualisieren", das wochenlang im Backlog liegt.

### Diffing

Was hat sich in den letzten Release Notes geändert? Zeigen Sie mir den Diff. In Git liefert `git diff v1.4..v1.5 -- docs/` genau das, was sich geändert hat. In einem Wiki klicken Sie sich einzeln durch Seitenhistorien, vergleichen gerenderte Ausgaben und hoffen, jede Bearbeitung zu erwischen.

### Automatisierung

Mit Dokumentation in Git können Sie Automatisierung bauen:

```bash
# Dokumentation finden, die seit 90 Tagen nicht aktualisiert wurde
git log --all --diff-filter=M --name-only --since="90 days ago" -- docs/ \
  | sort -u > recently_modified.txt

# Mit allen Dokumentationsdateien vergleichen
find docs/ -name "*.md" | sort > all_docs.txt

# Dateien, die seit 90 Tagen NICHT geändert wurden
comm -23 all_docs.txt recently_modified.txt
```

Versuchen Sie das mit einem Wiki. Sie müssten eine API ansprechen, Zeitstempel parsen und Paginierung handhaben — falls die API überhaupt Änderungsdaten freigibt.

## Der wahre Grund, warum Dokumentation nicht in Git ist

Es ist nicht technisch. Es ist historisch. Dokumentation existierte vor modernen DevOps-Praktiken. Wikis entstanden in den frühen 2000ern, als „Infrastructure as Code" nicht existierte und Versionskontrolle SVN bedeutete. Das Wiki-Modell — im Browser bearbeiten, in Datenbank speichern — ergab Sinn, als die Alternative darin bestand, Word-Dokumente per E-Mail zu verschicken.

Aber Engineering-Praktiken haben sich weiterentwickelt. Infrastruktur ging von manuell konfigurierten Servern zu deklarativem Code in Git. CI/CD ging von Jenkins-Jobs, die über eine Web-Oberfläche konfiguriert wurden, zu Pipeline-as-Code in YAML-Dateien. Konfiguration ging von Anwendungseinstellungsseiten zu Umgebungsvariablen und Konfigurationsdateien in Repositories.

Dokumentation ist der letzte Nachzügler. Nicht weil sie anders ist, sondern weil die Werkzeuge nicht mitgezogen haben. Static-Site-Generatoren lösten das „Docs in Git"-Problem für Entwickler, schlossen aber alle aus, die kein Terminal benutzen. Wikis lösten das „Jeder kann schreiben"-Problem, gaben aber die Versionskontrolle auf. Keine Seite hat die Lücke überbrückt — bis vor kurzem.

## Wie es richtig aussieht

Ein Dokumentations-Workflow, der Git respektiert, sollte so aussehen:

1. Autoren erstellen und bearbeiten Inhalte über eine Web-Oberfläche — kein Terminal erforderlich
2. Jedes Speichern erstellt einen Git-Commit — automatisch, unsichtbar
3. Entwickler können denselben Inhalt in ihrer IDE bearbeiten und zum selben Repository pushen
4. Beide Seiten bleiben synchron — keine Konflikte, kein manuelles Merging
5. Pull Requests funktionieren für Dokumentation genauso wie für Code
6. Die vollständige Git-Historie ist verfügbar: Blame, Diff, Log, Branch

Das ist nicht hypothetisch. Das [Content-Ledger-Muster](/blog/why-git-sync-breaks/) löst das Synchronisierungsproblem. Plattformen, die es implementieren, bieten Ihnen ein wiki-ähnliches Bearbeitungserlebnis mit einem Git-Repository als Backend.

Wenn Sie einen neuen Dokumentations-Workflow aufbauen — oder einen umbauen, der nicht funktioniert — beginnen Sie mit Git als Fundament. Wählen Sie Werkzeuge, die das Repository als Source of Truth behandeln, nicht als Exportziel. Ihr zukünftiges Ich, das prüft, was sich geändert hat und warum, wird froh sein, dass die Historie existiert.

Wie [die Git-Dokumentation selbst es formuliert](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control): Versionskontrolle zeichnet Änderungen an Dateien über die Zeit auf, damit Sie spezifische Versionen später abrufen können. Das gilt für Dokumentation genauso wie für Code. Vielleicht sogar mehr — denn Code hat Tests, um Regressionen abzufangen, aber Dokumentation hat nur das menschliche Gedächtnis.

Wenn Ihre Dokumentation es wert ist, geschrieben zu werden, ist sie es wert, versioniert zu werden. Speichern Sie sie in Git.

---

*Wenn Sie eine Dokumentationsplattform ausprobieren möchten, bei der Git die Source of Truth ist — nicht ein Nachgedanke — ist [DocPlatform](/install/) kostenlos und selbstgehostet. Ein Binary, keine Datenbank zu verwalten, bidirektionaler Git-Sync eingebaut.*
