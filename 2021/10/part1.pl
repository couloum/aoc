#!/usr/bin/perl -w

use Data::Dumper;
#use List::Util qw/min max/;

use strict;

############ MAIN ##################

my $file = "input.txt";
if (scalar(@ARGV) > 0 and -e $ARGV[0]) {
  $file = $ARGV[0];
}
open(FILE, $file) or die("Cannot open file: $file\n");

my %symbols_map = (
  '(' => ')',
  '[' => ']',
  '{' => '}',
  '<' => '>',
);
my %symbols_points = (
  ')' => 3,
  ']' => 57,
  '}' => 1197,
  '>' => 25137,
);

my $points = 0;
while (<FILE>) {
  chomp;
  my @symbols_pipe;
  for my $c (split(//, $_)) {
    if ($c =~ /[\(\[\{\<]/) {
      push(@symbols_pipe, $c);
    } else {
      my $last_symbol_open = pop(@symbols_pipe);
      my $expected_symbol_close = $symbols_map{$last_symbol_open};
      if ($c ne $expected_symbol_close) {
        print "Error: expected $expected_symbol_close, got $c\n";
        $points += $symbols_points{$c};
      }
    }
  }
}

close(FILE);

printf("\nResult: %d\n", $points);
