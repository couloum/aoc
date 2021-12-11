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
  ')' => 1,
  ']' => 2,
  '}' => 3,
  '>' => 4,
);

my @lines_points = ();
while (<FILE>) {
  chomp;
  my @symbols_pipe;
  my $valid = 1;
  for my $c (split(//, $_)) {
    if ($c =~ /[\(\[\{\<]/) {
      push(@symbols_pipe, $c);
    } else {
      my $last_symbol_open = pop(@symbols_pipe);
      my $expected_symbol_close = $symbols_map{$last_symbol_open};
      if ($c ne $expected_symbol_close) {
        # Discard invalid lines
        $valid = 0;
      }
    }
  }

  if ($valid == 0) {
    print "Discarding corrupted line: $_\n";
  } else {
    my $points = 0;
    # The line should be valid. Now, let's see what is in pipe;
    print "Remaining symbols: ", @symbols_pipe, "\n";
    while (@symbols_pipe) {
      my $symbol = pop @symbols_pipe;
      my $symbol_points = $symbols_points{$symbols_map{$symbol}};
      printf("  + Symbol %s: %d points\n", $symbol, $symbol_points);
      $points *= 5;
      $points += $symbol_points;
    }
    printf("  = Total points: %d\n", $points);
    push (@lines_points, $points);
  }
}

close(FILE);

@lines_points = sort({$a <=> $b} @lines_points);
printf("List of scores: %s\n", join(', ', @lines_points));

# Get middle score
my $score = $lines_points[(scalar(@lines_points)+1)/2-1];
printf("\nResult: %d\n", $score);
