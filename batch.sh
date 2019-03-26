mkdir -p out
mkdir -p pdf
mkdir -p tex
cd out
DEPUTES=$(psql grandelecture -tAc "SELECT format('%s,%s',replace(nom,' ','_'),replace(prenom,' ','_')) FROM deputes ORDER BY nom")
for D in $DEPUTES
do
  if [ ! -f ../pdf/$D.pdf ]
  then
    echo "data2latex $D"
    python ../data2latex.py "$D" > "$D.tex" \
    && xelatex "$D.tex" \
    && xelatex "$D.tex" \
    && mv "$D.pdf" ../pdf \
    && gzip -9 "$D.tex" && mv "$D.tex.gz" ../tex \
    && rm "$D".*
  fi

  if [ ! -f ../png/$D.png ]
  then
    convert ../pdf/$D.pdf[0] -resize 50% ../png/$D.png
  fi
done
