#!/usr/bin/env python3

import sys
import re
import json

import psycopg2

def txt2tex(md):
    if md:
        # guillemets
        md = md.encode('iso-8859-1','ignore').decode('iso-8859-1')
        t = md.replace('&amp;', ' \\& ').replace('&gt;', ' > ').replace('&lt;', ' < ')
        t = re.sub(r'([\&\%\$\#\_\{\}\~\^\\])', r'\\\1', t)
        t = t.replace('«', ' \\og ').replace('»', ' \\fg ')
        t = re.sub(r' +([\.,])', r'\1', t)
        t = t[0].upper() + t[1:]
        return(t)
    else:
        return ''


def out(data):
    print(data)


def reponse2tex(gdebat):
    global minutes

    for gd in gdebat:
        c = json.loads(gd[0])

        #  comptage des mots des réponses
        mots = 0
        for q in c['responses']:
            if q['formattedValue']:
                mots = mots + 10 + len(re.sub(r'[^A-Za-z0-1]',' ',q['formattedValue']).split())
        minutes = minutes + int(mots/150)

        #out('\\addcontentsline{toc}{section}{%s}' % (txt2tex(c['title']), ) + crlf)
        out(crlf+'\\needspace{4cm}')
        out('\\section{%s}' % (txt2tex(c['title']), ) + crlf)
        out('Code postal déclaré : \\textbf{%s} - Déposée le : %s - N\\degree %s (lecture : %s min.)\\newline'
            % (txt2tex(c['authorZipCode']), c['publishedAt'][:10], c['reference'], int(mots/150)) + crlf)
        for q in c['responses']:
            if q['formattedValue']:
                if (q['questionTitle'][:7] not in ['Si oui,','Pourquo']):
                    if prev in ['Oui','Non']:
                        out('\\newline')
                    out('\\needspace{2cm} \\noindent \\footnotesize{\\emph{%s}}' % txt2tex(q['questionTitle']))

                if q['formattedValue'] in ['Oui','Non']:
                    out('\\par \\noindent \\textbf{%s}' % txt2tex(q['formattedValue']))
                else:
                    if prev not in ['Oui','Non']:
                        out('\\par \\noindent')
                    else:
                        out(', ')
                    out('\\textbf{%s} \\newline' % txt2tex(q['formattedValue']).replace('. ','.\\newline '))
            prev = q['formattedValue']


crlf = '\x0d\x0a'
themes = ["Démocratie et citoyenneté",
          "Transition écologique",
          "Fiscalité et dépenses publiques",
          "Organisation de l'État et des services publics"]

pg = psycopg2.connect('dbname=grandelecture')
db = pg.cursor()

db.execute("SELECT prenom, nom, sexe FROM deputes WHERE nom = %s", (sys.argv[1],))
elu = db.fetchone()

db.execute("SELECT count(distinct(authorid)), count(*) FROM contrib JOIN elu_cp ON (authorzipcode=code_postal) WHERE nom = %s",
           (sys.argv[1],))
stats = db.fetchone()

db.execute("SELECT r.* FROM deputes d NATURAL JOIN ranks r WHERE nom = %s",
           (sys.argv[1],))
ranks = db.fetchone()


db.execute(
    'select count(d.*), count(distinct(date||d.code_postal||ville)) from (select distinct(code_postal) as code_postal from elu_cp where nom=%s) e natural join documents d ', (sys.argv[1],))
docs = db.fetchone()

print("""\\documentclass[a4paper, 12pt]{book}
\\usepackage[utf8]{inputenc}
\\usepackage[french]{babel}
\\usepackage{makeidx}
\\usepackage{hyperref}
\\usepackage{needspace}
\\usepackage{gensymb}
\\usepackage{fancyhdr}
\\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,      
    urlcolor=blue,
}


\\usepackage{geometry}
\\geometry{a4paper, portrait, margin=25mm}
\\setlength{\parindent}{0em}


\\title{Grande Lecture pour le Grand Débat}
\\author{Christian Quest}
\\date{2019-03-23} 

\\begin{document}
{

\\frontmatter

\\pagenumbering{gobble}
\\begin{center}
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
Ce document a été produit par l'équipe "Grande Lecture" lors du hackathon \\#HackGDN organisé à l'Assemblée Nationale le 23 mars 2019.\\par
Il est publié sous Licence Ouverte 2.0 et a été lui-même produit à partir des données ouvertes (opendata) suivantes:
\\begin{itemize}
    \\item données ouvertes du site granddebat.fr (Licence Ouverte)
    \\item base officielle des codes postaux (source: La Poste, sous licence ODbL 1.0)
    \\item table de correspondance des circonscriptions législatives (Ministère de l'Intérieur, Licence Ouverte)
    \\item le Répertoire National des Élus (Ministère de l'Intérieur, Licence Ouverte)
\\end{itemize}
\\pagebreak
\\section*{Préambule}

Le \\emph{Grand Débat National} a été l'occasion pour de nombreux citoyens de s'exprimer. Une part d'entre eux l'a fait sur la plateforme \\emph{granddebat.fr} mise en place par le gouvernement.\\newline
\\newline
\\textbf{Parmis les idées exprimées figure une demande de plus grande écoute et proximité avec les élus}.\\newline
\\newline
Ce projet de \\emph{Grande Lecture} a pour but de répondre partiellement à ce souhait en offrant aux élus une sélection aléatoire de contributions dans un format propice à la lecture intégrale de celles-ci.\\newline
\\newline
Par respect pour ces citoyens, nous vous demandons de prendre le temps de lire vous-même ces quelques contributions, qui ne représentent finalement qu'une infime partie des ce qui a été exprimé.\\newline
\\newline
Les pages suivantes contiennent une sélection aléatoire d'une centaine de contributions, 25 pour chacun des quatre thèmes, sélectionnées dans votre circonscription.

\\subsection*{Mise en garde}

Différentes analyses ont montré la très faible représentativité des contributions faites sur chacun des espaces où le Grand Débat a pu avoir lieu (sur le site officiel, sur des sites alternatifs, par courrier ou dans des réunions locales).\\newline
\\newline
À titre d'exemple, sur certaines circonscriptions législatives, le nombre de citoyens ayant déposé une contribution sur \\emph{granddebat.fr} varie dans un rapport de 50 (de moins d'une centaine à plus de 3000) !\\newline
\\newline
\\fbox{Le contenu qui vous est proposé à lire ici est donc à interpréter avec prudence.}

\\section*{Quelques chiffres}
L'ensemble des contributions publiques déposées sur \\emph{granddebat.fr} représente un total de plus de 160 millions de mots (soit plus de 300 fois Les Misérables de Victor Hugo).\\newline
Il faudrait plus de quatre ans et demi pour lire l'intégralité à raison de 8 heures par jour, 7 jours sur 7.
""" % ('Monsieur le député' if elu[2] == 'M' else 'Madame la députée',
       elu[0],
       elu[1],
       ) + crlf)

if stats[0] > 0 or docs[0]>0:
    out("\\section*{Dans votre circonscription}"+crlf)
    if stats[0] > 0 :
        out("""\\textbf{%s} personnes ont déposé \\textbf{%s} contributions libres sur \\emph{granddebat.fr} """ % (stats[0], stats[1]))
        if ranks :
            out(""" ce qui place votre circonscription en \\textbf{%s\\textsuperscript{%s}} place dans le département et \\textbf{%s\\textsuperscript{%s}} place au niveau national."""
                % (ranks[3], 'e' if ranks[3] > 1 else 'ère',
                ranks[2], 'e' if ranks[2] > 1 else 'ère'))
        out(' \\newline \\newline  ')

    if docs[0]>0:
        out("""\\textbf{%s} document%s concernant \\textbf{%s} réunion%s dans votre circonscription sont aussi disponibles sur\\newline \\href{https://granddebat.fr/pages/comptes-rendus-des-reunions-locales}{https://granddebat.fr/pages/comptes-rendus-des-reunions-locales}\\newline
""" % (docs[0], 's' if docs[0] > 1 else '', docs[1], 's' if docs[1] > 1 else ''))


out("""
\\clearpage

\\pagenumbering{roman}
\\tableofcontents

\\mainmatter

\\clearpage

""")


minutes = 0
for t in range(0, 4):
    out('\\chapter{%s} \\vspace{3cm}' % themes[t])
    db.execute("""
    SELECT * FROM (
        SELECT      j::text
        FROM        elu_cp e
        JOIN        contrib c ON (c.authorzipcode=e.code_postal)
        WHERE       nom = %s AND theme = %s AND length(c.j::text)<50000
        ORDER BY    random()
        LIMIT       50) as c
    GROUP BY 1
    LIMIT 25
    """, (sys.argv[1], str(t+1)))

    gdebat = db.fetchall()
    reponse2tex(gdebat)
    nb = len(gdebat)
    
    if nb<25 and stats[0] == 0:
        db.execute("""
        SELECT * FROM (
            SELECT      j::text
            FROM        contrib c
            WHERE       theme = %s AND length(c.j::text)<50000
                        AND (authorzipcode < '01' OR authorzipcode > '97')
            ORDER BY    random()
            LIMIT       50 ) as c
        GROUP BY 1
        LIMIT %s
        """, (str(t+1), 25-nb))

        gdebat = db.fetchall()
        reponse2tex(gdebat)
        nb = nb + len(gdebat)

    if nb<25:
        db.execute("""
        SELECT * FROM (
            SELECT      j::text
            FROM        contrib c
            WHERE       theme = %s AND length(c.j::text)<50000
            ORDER BY    random()
            LIMIT       50 ) as c
        GROUP BY 1
        LIMIT %s
        """, (str(t+1), 25-nb))

        gdebat = db.fetchall()
        reponse2tex(gdebat)


out("""

\\clearpage
\\pagestyle{fancy}
\\fancyhf{}
\\renewcommand{\\headrulewidth}{0pt}
\\hspace{0pt}\\vfill

\\noindent
\\rule{15cm}{0.25pt} \\newline
Ce document a été généré automatiquement le \\today{} à l'aide du langage \\LaTeX{} et des outils et logiciels libres suivants:
\\begin{itemize}
\\item langage \\href{https://www.python.org/}{python}
\\item base de donnée \\href{https://www.postgresql.org/}{PostgreSQL}
\\item outil de manipulation de fichier json \\href{https://stedolan.github.io/jq/}{"jq"}
\\item outil de manipulation de fichiers csv \\href{https://csvkit.readthedocs.io/en/latest/}{"csvkit"}
\\end{itemize}
Le code produit durant le hackathon pour ce projet \\emph{"Grande Lecture"} est disponible lui aussi sous une licence libre sur \\href{https://github.com/cquest/grande_lecture}{https://github.com/cquest/grande\\_lecture}
\\newline
\\textbf{Le temps total évalué pour sa lecture est d'au moins %s heures.}
\\newline
\\rule{15cm}{0.25pt}

\\vfill\\hspace{0pt}
\\pagebreak

}
\\end{document}

""" % int(minutes/60))
