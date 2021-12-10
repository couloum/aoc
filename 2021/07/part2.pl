#!/usr/bin/perl -w

#use Data::Dumper;
use List::Util qw/min max/;

use strict;

sub sum_fuel {
  my ($point, $arr) = @_;

  my $fuel = 0;
  for my $i (@$arr) {
    my $distance = abs($i - $point);
    $fuel += $distance * ($distance + 1) / 2 ;
  }
  return $fuel;
}

############ MAIN ##################

my $file = "input.txt";
if (scalar(@ARGV) > 0 and -e $ARGV[0]) {
  $file = $ARGV[0];
}
open(FILE, $file) or die("Cannot open file: $file\n");

my $line = <FILE>;
chomp($line);

close(FILE);

my @crabs = split(',', $line);

my $min_fuel = 99999999999;
for my $point (min(@crabs)..max(@crabs)) {
  my $fuel = sum_fuel($point, \@crabs);
  if ($fuel < $min_fuel) {
    $min_fuel = $fuel;
    print "Minimum fuel found at point ", $point, ": ", $fuel, "\n";
  }
}

printf("\nResult: %d\n", $min_fuel);
