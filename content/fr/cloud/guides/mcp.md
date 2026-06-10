---
title: "IA et integration MCP"
description: "Connectez Claude, Cursor et d'autres outils IA pour lire et modifier votre documentation."
weight: 5
---

# IA et integration MCP

Valoryx Cloud inclut un serveur MCP (Model Context Protocol) integre qui permet aux assistants IA d'interagir directement avec votre documentation.

## Qu'est-ce que MCP ?

MCP est un protocole standard qui permet aux outils IA de se connecter a des services externes. Voyez-le comme un moyen de donner a Claude ou Cursor la capacite de "voir" vos documents et d'y apporter des modifications — avec votre autorisation.

## Ce que l'IA peut faire avec vos documents

- **Lire** des pages pour repondre a des questions sur votre documentation
- **Rechercher** dans toutes les pages pour trouver du contenu pertinent
- **Creer** de nouvelles pages selon vos instructions
- **Modifier** des pages existantes (reecriture, amelioration, traduction)
- **Analyser** vos documents pour detecter les lacunes, les incoherences ou le contenu obsolete

## Mise en place

> **Statut :** l'endpoint MCP heberge pour Valoryx Cloud n'est **pas encore active** — les outils IA distants ne peuvent pas encore se connecter a `app.valoryx.dev`. Cette page sera mise a jour des sa mise en service. Sur une instance **auto-hebergee**, MCP fonctionne des aujourd'hui — suivez les etapes ci-dessous sur la machine qui execute DocPlatform.

### Auto-heberge : Claude Desktop

1. Allez dans **Workspace Settings** → **API Keys**
2. Creez une cle API — elle commence par `dp_live_` et n'est affichee qu'une seule fois
3. Dans `claude_desktop_config.json`, ajoutez :

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

4. Redemarrez Claude Desktop
5. Demandez a Claude : *"Qu'y a-t-il dans ma documentation ?"*

### Dans Cursor

Meme configuration — ajoutez la meme entree `docplatform` dans le fichier `.cursor/mcp.json` de votre projet.

## Outils MCP disponibles

Le serveur MCP fournit 26 outils :

| Outil | Description |
|---|---|
| `list_pages` | Lister toutes les pages d'un espace de travail |
| `read_page` | Lire le contenu d'une page specifique |
| `write_page` | Creer une page, ou la mettre a jour si elle existe deja |
| `update_page` | Mettre a jour une page existante |
| `delete_page` | Supprimer une page |
| `search` | Recherche plein texte dans toutes les pages |
| `list_workspaces` | Lister les espaces de travail disponibles |
| *...et plus encore* | Commentaires, metadonnees, arborescence |

## Securite

- Les cles API sont hachees (jamais stockees en clair)
- Vous controlez la portee de chaque cle : `read`, `write` et `delete`
- Revoquez les cles a tout moment depuis Workspace Settings
- Les echecs d'autorisation sont consignes, et chaque modification de contenu est tracee dans l'historique des pages
