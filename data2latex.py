#!/usr/bin/env python3

import sys
import re
import json

import psycopg2

def txt2tex(md):
    if md:
        # single/double quotes...
        md = md.replace("’", "'").replace(
            "‘", "'").replace('“', '"').replace('”','"').replace('^',' ')
        # non ISO
        md = md.encode('iso-8859-1','ignore').decode('iso-8859-1')
        # contrôle
        md = "".join(i for i in md if 31 < ord(i))
        # HTML
        t = md.replace('&amp;', ' \\& ').replace('&gt;', ' > ').replace('&lt;', ' < ')

        t = re.sub(r'([\&\%\$\#\_\{\}\~\^\\])', r'\\\1', t)
        t = t.replace('«', ' \\og ').replace('»', ' \\fg ')
        t = re.sub(r' +([\.,])', r'\1', t)
        if len(t)>1:
            t = t[0].upper() + t[1:]
        return(t)
    else:
        return ''


def out(data):
    print(data)


def select_contribs():
    db.execute("""
    SELECT * FROM (
        SELECT      j::text
        FROM        contrib_depute ce
        NATURAL JOIN contrib c
        WHERE       ce.nom = %s and ce.prenom = %s AND reference LIKE %s||'%%'
        ) as c
    GROUP BY 1
    """, (nom if geo is None else geo, prenom if geo is None else '', str(t+1),))
    return db.fetchall()


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
        out('\\begin{center}\\normalsize{Code postal déclaré : \\textbf{%s} - Déposée le : %s - N\\degree %s (lecture : %s min.)}\\end{center}'
            % (txt2tex(c['authorZipCode']), c['publishedAt'][:10], c['reference'], int(mots/150) if mots>150 else 'moins de 1') + crlf)
        nbrep = 0
        for q in c['responses']:
            if q['formattedValue'] and q['formattedValue'].strip() != '':
                nbrep = nbrep + 1
                if len(q['questionTitle']) >= 25 and q['questionTitle'] != 'Si oui, de quelle manière ?':
                    # question longue
                    out('\\needspace{2cm} \\footnotesize{\\emph{%s}}' % txt2tex(
                        q['questionTitle']))
                    # réponse oui/non
                    if q['formattedValue'].lower() in ['oui', 'non']:
                        out('\\textbf{%s}' % txt2tex(q['formattedValue'])+crlf)
                    else:
                        out('\\par \\small{\\textbf{%s}} \\par ' % txt2tex(
                            q['formattedValue']).replace('. ', '.\\newline'+crlf))
                else:
                    # question courte... on la supprime
                    out('\\small{\\textbf{%s}} \\par ' % txt2tex(
                        q['formattedValue']).replace('. ','.\\newline'+crlf))
        if nbrep == 0:
            out('\\emph{Aucune réponse donnée aux questions proposées.}')


# connexion à la base postgres
pg = psycopg2.connect('dbname=grandelecture')
db = pg.cursor()
params = sys.argv[1].replace('_', ' ').split(',')

if len(params)>1:
    # on a un nom,prenom de député en entrée
    nom = params[0]
    prenom = params[1]
    geo = None

    db.execute(
        "SELECT prenom, nom, sexe FROM deputes WHERE nom = %s AND prenom = %s", (nom, prenom))
    elu = db.fetchone()
    sous_titre = 'Exemplaire personnel destiné à\\newline ' + \
        ('Monsieur le député' if elu[2] == 'M' else 'Madame la députée')
    sous_titre2 = elu[0] + ' ' + elu[1]
    sous_titre3 = ", sélectionnées en priorité dans votre circonscription, sauf pour les circonscriptions législatives des français établis hors de France. Pour Paris, Lyon et Marseille, l'ensemble de la ville est pris en compte"
    sous_titre4 = elu[0] + ' ' + elu[1]
    db.execute("SELECT count(distinct(authorid)), count(*) FROM contrib JOIN elu_cp ON (authorzipcode=code_postal) WHERE nom = %s and prenom = %s",
               (nom, prenom))
    stats = db.fetchone()
    db.execute("SELECT r.* FROM deputes d NATURAL JOIN ranks r WHERE nom = %s AND prenom = %s",
           (nom, prenom))
    ranks = db.fetchone()

    db.execute(
        'select count(d.*), count(distinct(date||d.code_postal||ville)) from (select distinct(code_postal) as code_postal from elu_cp where nom = %s and prenom = %s) e natural join documents d ', (nom, prenom))
    docs = db.fetchone()
else:
    ## on a un code département ou code postal en entrée...
    nom = None
    geo = sys.argv[1]
    stats = None
    ranks = None
    docs = None
    if len(geo) == 5:
        # cas des codes postaux
        db.execute(
            "select string_agg(distinct(nom_de_la_commune),', ' order by nom_de_la_commune) from cp where code_postal = %s" , (geo,))
        cp = db.fetchone()
        sous_titre = 'Sélection de contributions issues\\newline du code postal'
        sous_titre2 = geo + '\\newline \\quad \\newline \\large ' + cp[0].replace(', ','\\newline ')
        sous_titre3 = ", sélectionnées en priorité par code postal"
        sous_titre4 = "Code Postal "+geo
    else:
        # c'est un département...
        db.execute(
            "select nom FROM departements WHERE code_insee = %s", (geo if geo != '20' else '2A',))
        dep = db.fetchone()
        sous_titre = 'Sélection de contributions issues\\newline du département'
        sous_titre2 = dep[0] + ((' (%s)' % geo) if geo < 'Z' else '')
        sous_titre3 = ", sélectionnées sur le département"
        sous_titre4 = dep[0]


crlf = '\x0d\x0a'
themes = ["Démocratie et citoyenneté",
          "Transition écologique",
          "Fiscalité et dépenses publiques",
          "Organisation de l'État et des services publics"]



out("""\\documentclass[a4paper, 10pt]{book}
\\usepackage[utf8]{inputenc}
\\usepackage[french]{babel}
\\usepackage{makeidx}
\\usepackage{hyperref}
\\usepackage{needspace}
\\usepackage{gensymb}
\\usepackage{fancyhdr}
\\hypersetup{
    colorlinks=true,
    linkcolor=black,
    filecolor=magenta,      
    urlcolor=blue,
}
\\usepackage{fancyhdr}

\\usepackage[headheight=13pt]{geometry}
\\geometry{a4paper, portrait, margin=25mm}
\\setlength{\parindent}{0em}

\\title{Grande Lecture pour le Grand Débat}
\\author{Christian Quest / Grande Lecture}
\\date{\\today} 

\\begin{document}
{

\\frontmatter

\\pagenumbering{gobble}

\\vspace*{\\fill}
{\\Huge
\\textbf{Grande Lecture du Grand Débat\\newline}
\\vspace{1cm}
\\rule{\\textwidth}{0.25pt}
%s\\newline \\par
\\emph{\\textbf{%s}}\\newline
}
\\vspace*{\\fill}

\\vfill
\\noindent
Ce document a été produit par l'équipe "Grande Lecture" lors du hackathon \\#HackGDN organisé à l'Assemblée Nationale le 23 mars 2019.\\par
Il est publié sous \\href{https://www.etalab.gouv.fr/licence-ouverte-open-licence}{\\textbf{Licence Ouverte 2.0}} et a été lui-même produit à partir des \\textbf{données ouvertes} (opendata) suivantes:
\\begin{itemize}
    \\item données ouvertes du site \\href{http://granddebat.fr}{\\emph{granddebat.fr}} (Licence Ouverte)
    \\item \\href{https://www.data.gouv.fr/fr/datasets/base-officielle-des-codes-postaux/}{base officielle des codes postaux} (source: La Poste, sous licence ODbL 1.0)
    \\item \\href{https://www.data.gouv.fr/fr/datasets/circonscriptions-legislatives-table-de-correspondance-des-communes-et-des-cantons-pour-les-elections-legislatives-de-2012-et-sa-mise-a-jour-pour-les-elections-legislatives-2017/}{table de correspondance des circonscriptions législatives} (Ministère de l'Intérieur, Licence Ouverte)
    \\item le \\href{https://www.data.gouv.fr/fr/datasets/5c34c4d1634f4173183a64f1}{Répertoire National des Élus} (Ministère de l'Intérieur, Licence Ouverte)
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
Les pages suivantes contiennent une sélection aléatoire d'une centaine de contributions, 25 pour chacun des quatre thèmes%s.

\\section*{Quelques chiffres}
L'ensemble des contributions publiques déposées sur \\emph{granddebat.fr} représente un total de plus de 160 millions de mots (soit plus de 300 fois Les Misérables de Victor Hugo).\\newline
Il faudrait plus de quatre ans et demi pour lire l'intégralité à raison de 8 heures par jour, 7 jours sur 7.
""" % (sous_titre, sous_titre2, sous_titre3) + crlf)

if not geo and (stats[0] > 0 or docs[0]>0):
    out("\\section*{Dans votre circonscription}"+crlf)
    if stats[0] > 0 :
        out("""\\textbf{%s} personnes ont déposé des contributions libres sur \\emph{granddebat.fr} """ % (stats[0], ))
        if ranks :
            out(""" ce qui place votre circonscription en \\textbf{%s\\textsuperscript{%s}} place dans le département et \\textbf{%s\\textsuperscript{%s}} place au niveau national."""
                % (ranks[3], 'e' if ranks[3] > 1 else 'ère',
                ranks[2], 'e' if ranks[2] > 1 else 'ère'))
        out(' \\newline \\newline  ')

    if docs[0]>0:
        out("""\\textbf{%s} document%s concernant \\textbf{%s} réunion%s dans votre circonscription sont aussi disponibles\\newline sur \\href{https://granddebat.fr/pages/comptes-rendus-des-reunions-locales}{https://granddebat.fr/pages/comptes-rendus-des-reunions-locales}
""" % (docs[0], 's' if docs[0] > 1 else '', docs[1], 's' if docs[1] > 1 else ''))


out("""
\\section*{Mise en garde}

Différentes analyses ont montré la très faible représentativité des contributions faites sur chacun des espaces où le Grand Débat a pu avoir lieu (sur le site officiel, sur des sites alternatifs, par courrier ou dans des réunions locales).\\newline
\\newline
À titre d'exemple, sur certaines circonscriptions législatives, le nombre de citoyens ayant déposé une contribution sur \\emph{granddebat.fr} varie dans un rapport de 50 (de moins d'une centaine à plus de 3000) !\\newline
\\newline
\\begin{center}
\\fbox{Le contenu qui vous est proposé à lire ici est donc à interpréter avec prudence.}
\\newline
\\newline
\\Large{\\emph{Bonne lecture !}}
\\end{center}

\\vfill

\\begin{center}
    \\Large{\\textbf{\\href{www.grande-lecture.fr}{www.grande-lecture.fr}}}
\\end{center}

\\clearpage

\\pagenumbering{roman}
\\pagestyle{fancy}
\\fancyhf{}
\\lhead{\\leftmark}
\\lfoot{www.grande-lecture.fr}
\\cfoot{\\thepage}
\\rfoot{%s}

\\tableofcontents

\\mainmatter
\\setlength{\parskip}{4pt}

\\clearpage

""" % (sous_titre4,))


minutes = 0
for t in range(0, 4):
    #  sélection et stockage des contributions tirées au sort de façon unique
    gdebat = select_contribs()
    manque = 25 - len(gdebat)

    if geo:
        if manque > 0:
            db.execute("""
            INSERT INTO contrib_depute SELECT j->>'reference', %s, '' FROM (
                SELECT      j
                FROM        contrib c
                LEFT JOIN   contrib_depute ce ON (ce.reference = c.reference and nom = %s)
                WHERE       c.authorzipcode LIKE %s||'%%'
                            AND c.reference LIKE %s||'%%'
                            AND length(c.j::text)<50000
                            AND ce.nom is NULL
                ORDER BY    random()
                LIMIT       25) as c
            GROUP BY 1
            LIMIT %s; 
            """, (geo, geo, geo, str(t+1), manque))
            pg.commit()
            gdebat = select_contribs()
            manque = 25 - len(gdebat)

        if manque > 0:
            dep = (geo[:2] if geo < '97' else geo[:3])
            db.execute("""
            INSERT INTO contrib_depute SELECT j->>'reference', %s, '' FROM (
                SELECT      j
                FROM        contrib c
                LEFT JOIN   contrib_depute ce ON (ce.reference = c.reference and nom = %s)
                WHERE       c.authorzipcode LIKE %s||'%%'
                            AND c.reference LIKE %s||'%%'
                            AND length(c.j::text)<50000
                            AND ce.nom is NULL
                ORDER BY    random()
                LIMIT       25) as c
            GROUP BY 1
            LIMIT %s;
            """, (geo, geo, dep, str(t+1), manque))
            pg.commit()
            gdebat = select_contribs()
            manque = 25 - len(gdebat)
    else:
        if manque > 0:
            db.execute("""
            INSERT INTO contrib_depute SELECT j->>'reference', %s, %s FROM (
                SELECT      j
                FROM        elu_cp e
                JOIN        contrib c ON (c.authorzipcode=e.code_postal)
                NATURAL LEFT JOIN contrib_depute
                WHERE       nom = %s AND prenom = %s AND reference LIKE %s||'%%' AND length(c.j::text)<50000
                            AND contrib_depute.nom is NULL
                ORDER BY    random()
                LIMIT       25) as c
            GROUP BY 1
            LIMIT %s; 
            """, (nom, prenom, nom, prenom, str(t+1), manque))
            pg.commit()
            gdebat = select_contribs()
            manque = 25 - len(gdebat)

        if manque > 0 and stats[0] == 0:
            db.execute("""
            INSERT INTO contrib_depute SELECT j->>'reference', %s, %s FROM (
                SELECT      j
                FROM        contrib c
                NATURAL LEFT JOIN contrib_depute
                WHERE       reference LIKE %s||'%%' AND length(c.j::text)<50000
                            AND (authorzipcode < '01' OR authorzipcode > '97')
                            AND contrib_depute.nom is NULL
                ORDER BY    random()
                LIMIT       25 ) as c
            GROUP BY 1
            LIMIT %s; 
            """, (nom, prenom, str(t+1), manque))
            pg.commit()
            gdebat = select_contribs()
            manque = 25 - len(gdebat)

        if manque > 0:
            db.execute("""
            INSERT INTO contrib_depute SELECT j->>'reference', %s, %s FROM (
                SELECT      j
                FROM        contrib c
                NATURAL LEFT JOIN contrib_depute
                WHERE       reference LIKE %s||'%%' AND length(c.j::text)<50000
                            AND contrib_depute.nom is NULL
                ORDER BY    random()
                LIMIT       25 ) as c
            GROUP BY 1
            LIMIT %s; 
            """, (nom, prenom, str(t+1), manque))
            pg.commit()
            gdebat = select_contribs()

    out('\\chapter{%s} \\vspace{3cm}' % themes[t])
    if len(gdebat) != 25:
        print(len(gdebat))
        exit()
        
    reponse2tex(gdebat)


out("""

\\clearpage
\\pagestyle{fancy}
\\fancyhf{}
\\renewcommand{\\headrulewidth}{0pt}
\\hspace{0pt}\\vfill

\\noindent
\\rule{\\textwidth}{0.25pt} \\newline
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
\\rule{\\textwidth}{0.25pt}

\\vfill\\hspace{0pt}

\\begin{center}
\\Large{\\textbf{\\href{www.grande-lecture.fr}{www.grande-lecture.fr}}}
\\end{center}

\\pagebreak

}
\\end{document}

""" % int(minutes/60))
