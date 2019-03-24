mkdir -p out
mkdir -p pdf
cd out
DEPUTES=$(psql grandelecture -tAc "SELECT replace(nom,' ','_') FROM deputes ORDER BY nom")
for D in $DEPUTES
do
  if [ ! -f ../pdf/$D.pdf ]
  then
    python ../data2latex.py "$D" > "$D.tex" \
    && xelatex "$D.tex" \
    && xelatex "$D.tex" \
    && mv "$D.pdf" ../pdf \
    && rm "$D".*
  fi
done
