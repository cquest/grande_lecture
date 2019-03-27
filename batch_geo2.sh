PDF=pdf/geo
TEX=tex/geo
PNG=png/geo
if [ ! -f ../$PDF/$1.pdf ]
then
    python ../data2latex.py "$1" > "$1.tex" \
    && xelatex "$1.tex" \
    && xelatex "$1.tex" \
    && mv "$1.pdf" ../$PDF \
    && gzip -9 "$1.tex" && mv "$1.tex.gz" ../$TEX \
    && rm "$1".* \
    && convert ../$PDF/$1.pdf[0] -resize 50% ../$PNG/$1.png
fi
