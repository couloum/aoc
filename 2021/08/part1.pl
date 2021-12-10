#!/usr/bin/perl -w

#use Data::Dumper;
#use List::Util qw/min max/;

use strict;

############ MAIN ##################

my $file = "input.txt";
if (scalar(@ARGV) > 0 and -e $ARGV[0]) {
  $file = $ARGV[0];
}
open(FILE, $file) or die("Cannot open file: $file\n");

my $nb_searched_digits = 0;
while (<FILE>) {
  chomp;
  if ($_ =~ /\| (.*)/) {
    my @digits = split(' ', $1);
    foreach my $digit (@digits) {
      $nb_searched_digits++ if (length($digit) =~ /^[2347]$/)
    }
  }
}

close(FILE);


printf("\nResult: %d\n", $nb_searched_digits);
