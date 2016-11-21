set term png size 1000,800
#set size 0.9,0.
set output "6.png"
set yrange [0:8]
Leg="Frequency Count"
set xtic rotate by 45 right out
set boxwidth 0.2 absolute
set style fill solid 1.0 noborder
plot 'data' using 2:xtic(1) title Leg  smooth frequency with boxes 
