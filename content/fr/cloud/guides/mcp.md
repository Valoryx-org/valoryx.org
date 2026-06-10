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

### Dans Claude Desktop

1. Allez dans **Workspace Settings** → **API Keys**
2. Creez une cle API (Read & Write ou Read Only)
3. Dans les parametres de Claude Desktop, ajoutez ce serveur MCP :

```json
{
  "mcpServers": {
    "valoryx-docs": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-remote", "https://app.valoryx.dev/api/v1/mcp"],
      "env": {
        "API_KEY": "your-api-key-here"
      }
    }
  }
}
```

4. Redemarrez Claude Desktop
5. Demandez a Claude : *"Qu'y a-t-il dans ma documentation ?"*

### Dans Cursor

Meme configuration — ajoutez le serveur MCP dans les parametres de Cursor et utilisez la meme cle API.

## Outils MCP disponibles

Le serveur MCP fournit 26 outils :

| Outil | Description |
|---|---|
| `list_pages` | Lister toutes les pages d'un espace de travail |
| `read_page` | Lire le contenu d'une page specifique |
| `create_page` | Creer une nouvelle page |
| `update_page` | Mettre a jour une page existante |
| `delete_page` | Supprimer une page |
| `search` | Recherche plein texte dans toutes les pages |
| `list_workspaces` | Lister les espaces de travail disponibles |
| *...et plus encore* | Commentaires, metadonnees, arborescence |

## Securite

- Les cles API sont hachees (jamais stockees en clair)
- Vous controlez la portee : Read Only ou Read & Write
- Revoquez les cles a tout moment depuis Workspace Settings
- Toutes les requetes MCP sont consignees dans le journal d'audit
