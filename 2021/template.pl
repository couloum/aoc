#!/usr/bin/perl -w

#use Data::Dumper;
#use List::Util qw/min max/;

use strict;

my $DEBUG = 0;


sub print_2d_map {
  my ($map) = @_;

  for (my $y = 0; $y < scalar($map); $y++) {
    for (my $x = 0; $x < scalar($map->[$y]); $x++) {
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

############ MAIN ##################


my $file = "input.txt";
while(scalar(@ARGV)) {
  my $arg = pop(@ARGV);
  if (-f $arg) {
    $file = $arg;
  }
  if ($arg eq "-d") {
    $DEBUG++;
  }
}
open(FILE, $file) or die("Cannot open file: $file\n");

my $result = 0;

while (<FILE>) {
  debug(3, "Read line: $_");
  chomp;
}

close(FILE);

debug("\n===================================================================\n");
printf("Result: %d\n", $result);
