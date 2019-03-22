# Grande Lecture

**Projet visant à faciliter la lecture par les élus des contributions publiques déposées sur le site officiel granddebat.fr**


## Pourquoi ?

La masse de contributions déposées sur le site en ligne mis en place par le gouvernement à l'occasion du grand débat national rend son analyse particulièrement délicate.

Les contributions libres sont parfois très riches et peuvent difficilement se résumer à une analyse automatique par des outils d'intelligence artificielle.

Par respect pour le temps passé par ces citoyens à rédiger ces contributions, il est normal que celles-ci soient lues, tout particulièrement par des élus.

En effet, une des idées qui se dégage à la lecture (humaine) des contributions est la déconnexion de certains élus. Une lecture directe par ceux-ci de ces contributions est une première réponse possible.

Le projet ici est donc limité à la lecture, rien d'autre, pas d'annotation, pas de statistiques ou analyses.


## Comment ?

Pour chaque élu, une sélection d'une centaine de contributions est faite aléatoirement, en privilégiant les réponses provenant de sa circonscription (3/4).

Pour en faciliter au maximum la lecture, celles-ci sont mises en page sous forme de documents PDF (ou autre format) permettant une lecture "papier" ou sur écran (liseuse ou ordinateur).

Pour les députés, ce fichier PDF leur sera envoyé directement par courrier électronique.


## Les données...

- **contributions**: La source principale de données est bien entendu l'export des contributions publié en opendata. Ces données contiennent le *code postal* indiqué lors de l'inscriptions sur granddebat.fr
- **code postal**: il permet de retrouver la ou les *communes* correspondantes
- **communes**: le Ministère de l'Intérieur publie les données des regroupements de communes en *circonscriptions* 
- **circonscription**: Le Répertoire National des Élus permet de passer de la circonscription à l'*élu*
- **élu**: son adresse email est récupérée sur le site de l'Assemblée

## Le code et les outils...

Toutes les données sont importées dans une base postgresql et des vues sont crées pour faire le lien entre les sources de données.

Un script python génère les fichiers PDF à l'aide du langage LaTeX.

L'envoi des emails peut s'automatiser avec un script bash ou python.
