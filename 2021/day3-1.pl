#!/usr/bin/perl -w

use strict;

my $file = "day3-input";
open(FILE, $file) or die("Cannot open file: $file\n");

my @t=(
  {0 => 0, 1 => 0},
  {0 => 0, 1 => 0},
  {0 => 0, 1 => 0},
  {0 => 0, 1 => 0},
  {0 => 0, 1 => 0},
  {0 => 0, 1 => 0},
  {0 => 0, 1 => 0},
  {0 => 0, 1 => 0},
  {0 => 0, 1 => 0},
  {0 => 0, 1 => 0},
  {0 => 0, 1 => 0},
  {0 => 0, 1 => 0}
);

my $g=0;
my $e=0;
my $gs=""; #gamma
my $es=""; #epsilon

while (<FILE>) {
  $_ =~ s/\n$//;

  for my $i (0..11) {
    my $d = substr($_, $i, 1);
    $t[$i]{$d}++;
  }
}

for my $i (0..11) {
  $g<<=1;
  $e<<=1;
  if ($t[$i]{0} > $t[$i]{1}) {
    $gs.="0";

    $e+=1;
    $es.="1";
  } else {
    $g+=1;
    $gs.="1";

    $es.="0";
  }
}

printf("Result: %d [g=%s (%d) e=%s (%d)]\n", $g*$e, $gs, $g, $es, $e);
