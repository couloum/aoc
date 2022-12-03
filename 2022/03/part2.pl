#!/usr/bin/perl -w

use Data::Dumper;
#use List::Util qw/min max/;

use strict;

my $DEBUG = 0;


sub print_2d_map {
  my ($map) = @_;

  for (my $y = 0; $y < scalar(@$map); $y++) {
    for (my $x = 0; $x < scalar(@{$map->[$y]}); $x++) {
      print $map->[$y][$x];
    }
    print "\n";
  }
}

sub debug {
  my $level = 1;
  if ($_[0] =~ /^\d+$/) {
    $level =$_[0];
    shift;
  }
  print @_ if ($DEBUG >= $level);
}

sub find_item {
  my ($e1, $e2, $e3) = @_;

  debug(2, "Analyzing the following backpacks:\n  $e1\n  $e2\n  $e3\n");

  # Iterate over backpack and see if item is present in 2 other backpacks
  foreach my $item (split(//, $e1)) {
    debug(3, "Searching item $item in all backpacks\n");
    return $item if (index($e2, $item) >= 0 and index($e3, $item) >= 0);
  }

  return 0;
}

sub get_prio {
  my $item = shift;
  my $ord = ord($item);

  return $ord - 96 if ($ord >= 96); # Lowercase : a=1, z=26
  return $ord - 64 + 26;            # Uppercase : A=27, Z=52
}

############ MAIN ##################


my $file = "input.txt";
while(scalar(@ARGV)) {
  my $arg = pop(@ARGV);
  if ($arg eq "-d") {
    $DEBUG++;
  } elsif ($arg eq "-dd") {
    $DEBUG=2;
  } elsif ($arg eq "-ddd") {
    $DEBUG=3;
  } elsif ($arg =~ /^(-h|--help)$/) {
    print "Usage: <script> [-f INPUT-FILE] [-d]\n";
    print "You can add up to 3 'd' for more debug\n";
    exit(0);
  } elsif ($arg =~ /^-/) {
    die "Invalid parameter: $arg\n";
  } else {
    if (-f $arg) {
      $file = $arg;
    } else {
      die "Invalid file: $arg\n";
    }
  }
}
open(FILE, $file) or die("Cannot open file: $file\n");

my $result = 0;

while (<FILE>) {
  debug(3, "Read line: $_");
  chomp;
  my $e1 = $_;
  my $e2 = <FILE>; chomp $e2;
  my $e3 = <FILE> ; chomp $e3;

  # Get item present in 3 backpacks
  my $item = find_item($e1, $e2, $e3);
  die("Error!\n") if ($item eq "0");

  # Get priority of the item
  my $prio = get_prio($item); 

  $result += $prio;
  debug("Item present in both compartments: $item (priority: $prio / $result)\n");
}

close(FILE);

debug("\n===================================================================\n");
printf("Result: %d\n", $result);
