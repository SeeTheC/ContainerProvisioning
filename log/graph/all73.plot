set term png size 1000,800
#set size 0.9,0.

set output "cp1479681234073.png"

set yrange [0:1]
set xrange [0:25]
set xtics  1
set ytics  0.1
set grid ytics
Leg="Utilization"
set boxwidth 0.2 absolute
set style fill solid 1.0 noborder
plot 'cp1479681234073' using 1:2 title Leg  with boxes 
