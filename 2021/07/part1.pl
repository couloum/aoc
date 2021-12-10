#!/usr/bin/perl -w

#use Data::Dumper;
#use List::Util qw/min max/;

use strict;

sub median {
  my @vals = sort {$a <=> $b} @_;
  my $len = @vals;
  if($len%2) {
    return $vals[int($len/2)];
  } else {
    return ($vals[int($len/2)-1] + $vals[int($len/2)])/2;
  }
}

sub sum_distance {
  my ($point, $arr) = @_;

  my $distance = 0;
  for my $i (@$arr) {
    $distance += abs($i - $point);
  }
  return $distance;
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

my $median = median(@crabs);
my $distance = sum_distance($median, \@crabs);

printf("\nResult: %d\n", $distance);
