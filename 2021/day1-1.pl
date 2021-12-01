#!/usr/bin/perl -w

use strict;

open(FILE, "day1-input") or die("Cannot open file: day1-input\n");

my $nbinc=0;
my $nb=0;
my $lastval=-1;
while (<FILE>) {
  $_ =~ s/\s+$//;

  $nb++;

  print $nb, ": ", $_;

  if ($lastval < 0) {
    $lastval = $_;
    print " (=)\n";
    next;
  }

  if ($_ > $lastval) {
    $nbinc++;
    print " (>)\n";
  } else {
    print " (<)\n";
  }
  
  $lastval=$_;
}

print "\nResult: $nbinc / $nb\n";
