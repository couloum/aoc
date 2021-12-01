#!/usr/bin/perl -w

use List::Util qw/sum/;
use strict;

open(FILE, "day1-input") or die("Cannot open file: day1-input\n");

my $nbinc=0;
my $nb=0;
my $lastval=-1;
my @buffer;
while (<FILE>) {
  $_ =~ s/\s+$//;

  push @buffer, ($_);
  $nb++;
  next unless scalar(@buffer) == 3;

  my $sum = sum(@buffer);
  print $nb, ": ", join('+', @buffer), " = $sum";
  shift @buffer;

  if ($lastval < 0) {
    $lastval = $sum;
    print " (=)\n";
    next;
  }

  if ($sum > $lastval) {
    $nbinc++;
    print " (>)\n";
  } else {
    print " (<)\n";
  }
  
  $lastval=$sum;
}

print "\nResult: $nbinc / $nb\n";
