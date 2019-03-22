#!/usr/bin/env python3

import sys
import re
import json

import psycopg2

def txt2tex(md):
    if md:
        # guillemets
        t = re.sub(r'([\&\%\$\#\_\{\}\~\^\\])', r'\\\1', md)
        t = t.replace('«', ' \\og ').replace('»', ' \\fg ')
        t = t.replace('\n\n+', '\\par'+crlf)
        t = t.replace('\n', '\\newline'+crlf)
        t = t[0].upper() + t[1:]
        return(t)
    else:
        return ''


def out(data):
    print(data)


crlf = '\x0d\x0a'
themes = ["Démocratie et citoyenneté",
          "Transition écologique",
          "Fiscalité et dépenses publiques",
          "Organisation de l'État et des services publics"]

pg = psycopg2.connect('dbname=grandelecture')
db = pg.cursor()

db.execute("SELECT prenom, nom, sexe FROM deputes WHERE nom = %s", (sys.argv[1],))

elu = db.fetchone()

print("""\\documentclass[a4paper, 12pt]{book}
\\usepackage[utf8]{inputenc}
\\usepackage[french]{babel}
\\usepackage{makeidx}
\\usepackage{hyperref}
\\usepackage{needspace}
\\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,      
    urlcolor=blue,
}


\\title{Grande Lecture pour le Grand Débat}
\\author{Christian Quest}
\\date{2019-03-23} 

\\begin{document}
{

\\frontmatter

\\pagenumbering{gobble}
\\begin{center}
\\vspace{5cm}
\\Huge
\\noindent\\textbf{Grande Lecture\\newline
du Grand Débat\\newline}
\\newline
Exemplaire personnel destiné à\\newline
\\newline
%s\\newline
\\newline
\\emph{\\textbf{%s %s}}\\newline
\\end{center}

\\vspace{5cm}
\\noindent
Ce document a été produit par l'équipe "Grande Lecture" lors du hackathon \\#HackGDN organisée à l'Assemblée Nationale le 23 mars 2019.\\par
\\pagebreak
\\section*{Préambule}

Le \\emph{Grand Débat National} a été l'occasion pour de nombreux citoyens de s'exprimer. Une part d'entre eux l'a fait sur la plateforme \\emph{granddebat.fr} mise en place par le gouvernement.\\newline
\\newline
\\textbf{Parmis les idées exprimées figure une demande de plus grande écoute et proximité avec les élus}.\\newline
\\newline
Ce projet de \\emph{Grande Lecture} a pour but de répondre partiellement à ce souhait en offrant aux élus une sélection aléatoire de contributions dans un format propice à la lecture intégrale de celles-ci.\\newline
\\newline
Par respect pour ces citoyens, nous vous demandons de prendre le temps de lire vous même ces quelques contributions, qui ne représentent finalement qu'une infime partie des ce qui s'est exprimé.\\newline
\\newline
Les pages suivantes contiennent une sélection aléatoire d'une centaine de contributions, 25 pour chacun des 4 thèmes, sélectionnées dans votre circonscription.

\\subsection*{Quelques chiffres}
L'ensemble des contributions publiques déposées sur \\emph{granddebat.fr} représente un total de plus de 160 millions de mots (plus de 300 fois Les Misérables de Victor Hugo).\\newline
Il faudrait plus de 4 ans et demi pour lire l'intégralité à raison de 8 heures par jours, 7 jours sur 7.
\\subsection*{Mise en garde}

Différentes analyses ont montré la très faible représentativité des contributions faites sur chacun des espaces où le Grand Débat a pu avoir lieu (sur le site officiel, sur des sites alternatifs, par courrier ou dans des réunions locales).\\newline
\\newline
À titre d'exemple, sur certaines circonscriptions législatives, le nombre de citoyen qui a déposé une contribution sur \\emph{granddebat.fr} varie dans un rapport de 50 (de moins d'une centaine à plus de 3000) !\\newline
\\newline
\\fbox{Le contenu qui vous est proposé à lire ici est donc à interpreter avec prudence.}
\\clearpage

\\pagenumbering{roman}
\\tableofcontents

\\mainmatter

\\clearpage

""" % ('Monsieur le député' if elu[2]=='M' else 'Madame la députée', elu[0], elu[1]) +crlf)


for t in range(0,4):
    out('\\chapter{%s} \\vspace{3cm}' % themes[t])
    db.execute("""
    SELECT      c.*
    FROM        elu_cp e
    JOIN        contrib c ON (c.authorzipcode=e.code_postal)
    WHERE       nom = %s and theme = %s
    ORDER BY    random()
    LIMIT       25
    """, (sys.argv[1], str(t+1)))

    gdebat = db.fetchall()
    for gd in gdebat:
        c = gd[0]

        #out('\\addcontentsline{toc}{section}{%s}' % (txt2tex(c['title']), ) + crlf)
        out('\\needspace{3cm}')
        out('\\section{%s}' % (txt2tex(c['title']), ) + crlf+crlf)
        out('\\noindent Code postal: \\textbf{%s} - Déposée le : %s\\newline' % (txt2tex(c['authorZipCode']), c['publishedAt'][:10]) + crlf+crlf)
        for q in c['responses']:
            if q['formattedValue']:
                out('\\needspace{2cm}')
                if q['formattedValue'] in ['Oui','Non']:
                    out('\\noindent \\emph{%s} ' % txt2tex(q['questionTitle']))
                else:
                    out('\\noindent \\emph{%s} \\newline ' % txt2tex(
                        q['questionTitle']) + crlf)
                out('\\noindent \\textbf{%s} \\newline' % txt2tex(q['formattedValue']) + crlf)
        out('\\rule{4cm}{0.25pt}')

    if len(gdebat)<25:
        db.execute("""
        SELECT      c.*
        FROM        contrib c
        WHERE       theme = %s
        ORDER BY    random()
        LIMIT       %s
        """, (str(t+1), 25-len(gdebat)))

        gdebat = db.fetchall()
        for gd in gdebat:
            c = gd[0]

            #out('\\addcontentsline{toc}{section}{%s}' % (txt2tex(c['title']), ) + crlf)
            out('\\needspace{3cm}')
            out('\\section{%s}' % (txt2tex(c['title']), ) + crlf+crlf)
            out('\\noindent Code postal: \\textbf{%s} - Déposée le : %s\\newline' % (
                txt2tex(c['authorZipCode']), c['publishedAt'][:10]) + crlf+crlf)
            for q in c['responses']:
                if q['formattedValue']:
                    out('\\needspace{2cm}')
                    if q['formattedValue'] in ['Oui', 'Non']:
                        out('\\noindent \\emph{%s} ' % txt2tex(q['questionTitle']))
                    else:
                        out('\\noindent \\emph{%s} \\newline ' % txt2tex(
                            q['questionTitle']) + crlf)
                    out('\\noindent \\textbf{%s} \\newline' %
                        txt2tex(q['formattedValue']) + crlf)


out("""

\\backmatter
\\pagenumbering{gobble}
\\pagebreak
\\hspace{0pt}\\vfill

\\noindent
\\rule{15cm}{0.25pt}
Ce document a été généré automatiquement le \\today\\newline
à l'aide du langage \\LaTeX et des outils et logiciels libres suivants:
\\begin{itemize}
\\item langage \\href{https://www.python.org/}{python}
\\item base de donnée \\href{https://www.postgresql.org/}{PostgreSQL}
\\item outil de manipulation de fichier json \\href{https://stedolan.github.io/jq/}{"jq"}
\\item outil de manipulation de fichiers csv \\href{https://csvkit.readthedocs.io/en/latest/}{"csvkit"}
\\end{itemize}
Le code produit durant le hackathon pour ce projet \\emph{"Grande Lecture"} est disponible sur \\href{https://github.com/cquest/grande_lecture}{https://github.com/cquest/grande\\_lecture}.
\\newline
\\rule{15cm}{0.25pt}

\\vfill\\hspace{0pt}
\\pagebreak

}
\\end{document}

""")
