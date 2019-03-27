PDF=pdf/geo
TEX=tex/geo
PNG=png/geo
mkdir -p out
mkdir -p $PDF
mkdir -p $TEX
mkdir -p $PNG
cd out
echo "$(seq -w 01 95) $(seq -w 971 974)" \
| sed 's/ /\n/g' \
| parallel -j 24 sh ../batch_geo2.sh {}

psql grandelecture -At -c 'select distinct(code_postal) from cp order by 1' \
| parallel -j 12 sh ../batch_geo2.sh {}
