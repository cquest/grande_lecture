createdb grandelecture

# import liste des circonscriptions / communes
psql grandelecture -c "create table circo (CODE_DPT text,NOM_DPT text,CODE_COMMUNE text,NOM_COMMUNE text,CODE_CIRC_LEGISLATIVE text,CODE_CANTON text,NOM_CANTON text);"
psql grandelecture -c "\copy circo from Table_de_correspondance_circo_legislatives2017-1.csv with (format csv, header true)"
psql grandelecture -c "
update circo set code_dpt = right('00'||code_dpt,2);
update circo set code_commune = code_dpt|| right('000'||code_commune,3);
update circo set code_circ_legislative = right('00'||code_circ_legislative,2);
"

# import des codes INSEE des communes / codes postaux
ogr2ogr PG:"dbname=granddebat" -nln cp laposte_hexasmal.geojson -overwrite

# génère la liste des contributeurs
rm -f temp
for f in *.csv.gz
do
  echo $f
  zcat $f | csvcut -c authorId,authorType,authorZipCode -z 250000 | tail -n +2 >> temp
done
echo 'authorId,authorType,authorZipCode' > authors.csv
sort -u temp | uniq >> authors.csv

# import liste des contributeurs
psql grandelecture -c "create table author (authorId text,authorType text,authorZipCode text) ;"
psql grandelecture -c "\copy author from authors.csv with (format csv, header true)"

# liste des députes
csvcut 8-rne-deputes.txt -t -e iso8859-1 -c 1,3,5,6,7 -K 1 > deputes.csv
psql grandelecture -c "create table deputes (dep text, circo text, nom text, prenom text, sexe text)"
psql grandelecture -c "\copy deputes from deputes.csv with (format csv, header true)"

# vue élu + email / circo / commune / cp
psql grandelecture -c "create view elu_cp as select dep,circo,nom,prenom,sexe,code_commune,code_postal,lower(format('%s.%s@assemblee-nationale.fr',replace(unaccent(prenom),' ',''),replace(unaccent(nom),' ',''))) as email from deputes d join circo c on (code_dpt=dep and code_circ_legislative=circo) join cp on (code_commune_insee=code_commune) ;"

# import contributions
psql grandelecture -c "drop table if exists contrib ; create table contrib (j json);"
for j in *.json
do
  jq . $j | grep -v '"value"'  | jq . -c | psql grandelecture -c "copy contrib from stdin with (format csv, delimiter e'\x01', quote e'\x02', escape e'\x03')"
done
# extraction id, authorid, authorzipcode depuis le json pour index
psql grandelecture -c "
alter table contrib add authorid text;
alter table contrib add authorzipcode text;
alter table contrib add reference text;
update contrib set (authorid,authorzipcode,reference) = (j->>'authorId', j->>'authorZipCode', j->>'reference');
create index on contrib (authorzipcode);
"

#  qui lit quoi
psql grandelecture -c "
CREATE TABLE contrib_depute (reference text, nom text);
CREATE INDEX ON contrib_depute (nom);
"
#  Classement des participations par circo/dep
psql grandelecture -c "create MATERIALIZED VIEW ranks as select dep,circo, rank() over (ORDER BY count(distinct(authorid)) DESC) rank_fr, rank() over (partition by dep ORDER BY count(distinct(authorid)) DESC) rank_dep, count(distinct(authorid)), count(distinct(j->>'id')) as nb_contrib from contrib join elu_cp on (code_postal=authorzipcode) group by dep,circo;"

#  Annotations
psql grandelecture -c "
drop table if exists annotations ;
create table annotations (theme text, ref text, question text, tag text, annotateur int, poids float);
create index on annotations (question);
"
psql grandelecture -c "\copy annotations from 'actions/actions.csv' with (format csv, header true)"

