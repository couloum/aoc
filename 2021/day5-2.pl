#!/usr/bin/perl -w

use Data::Dumper;
use List::Util qw/min max/;

use strict;

sub update_map {
  my ($x1, $y1, $x2, $y2, $map_ref) = @_;

  # Check if hydrothermal vent is horizontal, vertical or diagonal
  if ($x1 == $x2) {
    # Vertical
    my $start = min($y1, $y2);
    my $end = max($y1, $y2);
    foreach my $y ($start..$end) {
      $map_ref->{$x1}{$y}++;
    }
  } elsif ($y1 == $y2) {
    # Horizontal
    my $start = min($x1, $x2);
    my $end = max($x1, $x2);
    foreach my $x ($start..$end) {
      $map_ref->{$x}{$y1}++;
    }
  } else {
    # Get increment for x and y
    my $x_incr = ($x1 < $x2) ? 1 : -1;
    my $y_incr = ($y1 < $y2) ? 1 : -1;
    my $y = $y1;

    #printf("Diagonal: %d,%d -> %d,%d\n", $x1,$y1,$x2,$y2);
    for (my $x = $x1; $x != $x2 + $x_incr; $x += $x_incr) {
      #printf("  * Set point: %d,%d\n", $x, $y);
      $map_ref->{$x}{$y}++;
      $y+=$y_incr;
    }
  }
}

sub count_points_in_map {
  my ($map_ref, $minval) = @_;

  my $nb = 0;
  for my $x (0..999) {
    for my $y (0..999) {
      $nb++ if ($map_ref->{$x}{$y} >= $minval);
    }
  }
  return $nb;
}

############ MAIN ##################

my $file = "day5-input";
open(FILE, $file) or die("Cannot open file: $file\n");


# Create a map 1000x1000
my %map;

foreach my $x (0..999) {
  $map{$x} = {};
  foreach my $y (0..999) {
    $map{$x}{$y} = 0;
  }
}

# Read input
while (<FILE>) {
  $_ =~ s/\n//;

  if ($_ =~ /^(\d+),(\d+) -> (\d+),(\d+)$/) {
    my $x1 = $1;
    my $y1 = $2;
    my $x2 = $3;
    my $y2 = $4;

    update_map($x1, $y1, $x2, $y2, \%map);
  }
}

#print Dumper(%map);

printf("Result: %d\n", count_points_in_map(\%map, 2));
