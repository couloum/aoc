#!/usr/bin/perl -w

use strict;

my $file = "day2-input";
open(FILE, $file) or die("Cannot open file: $file\n");

my $h = 0; #Horizontal position
my $d = 0; #Depth
my $a = 0; #Aim

my $nb = 0;

while (<FILE>) {
  $_ =~ s/\n$//;

  printf("$nb: (%-15s) - ",$_);

  if ($_ =~ /forward (\d+)/) {
    $h+= $1;
    $d+=$a*$1;
    print "FWD:   $1";
  } elsif ($_ =~ /down (\d+)/) {
    $a+=$1;
    print "DOWN:  $1";
  } elsif ($_ =~/up (\d+)/) {
    print "UP:    $1";
    $a-=$1;
  }

  print " - H:$h D:$d\n";
  $nb++;
}

print "\nResult: ", $h * $d, "\n";
