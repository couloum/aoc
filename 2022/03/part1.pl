#!/usr/bin/perl -w

#use Data::Dumper;
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
  my $items = shift;

  # Get size of string
  my $s = length($items);
  debug(2, "List: $items. Length: $s\n");
  
  # Iterate over 2nd half of the string
  for (my $i = $s/2; $i < $s ; $i++) {
    # Find if one letter is in first half
    my $l = substr($items, $i, 1);
    my $idx = index($items, $l);
    debug(3, "Search item $l. Found at position $idx\n");
    if ($idx >= 0 and $idx < $s / 2) {
      return $l;
    }
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

  # Get item in both compartment
  my $item = find_item($_);
  die("Error!\n") if ($item eq "0");

  # Get priority of the item
  my $prio = get_prio($item); 

  $result += $prio;
  debug("Item present in both compartments: $item (priority: $prio / $result)\n");
}

close(FILE);

debug("\n===================================================================\n");
printf("Result: %d\n", $result);
