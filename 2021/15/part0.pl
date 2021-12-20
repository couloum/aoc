#!/usr/bin/perl -w

use Data::Dumper;
use List::Util qw/min max/;

use strict;

my $DEBUG = 0;

$|++;

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

sub print_path {
  my ($map, $visited_cells) = @_;

  for (my $y = 0; $y < scalar(@$map); $y++) {
    for (my $x = 0; $x < scalar(@{$map->[$y]}); $x++) {
      if (grep(/^$x,$y$/, @$visited_cells)) {
        print "\e[31m";
      }
      print $map->[$y][$x];
      print "\e[0m";
    }
    print "\n";
  }
}

sub find_shortest_path {
  my ($map, $x, $y, $score, $min_score, $visited_cells) = @_;

  # Return -1 if $x and $y have already been visited
  return -1 if (grep /^$x,$y$/, @$visited_cells);

  # Add current cell to visited cells
  push (@$visited_cells, "$x,$y");

  # Add current cell to score unless it is starting cell
  $score += $map->[$y][$x] unless ($x == 0 and $y == 0);

  debug 3, "$x,$y: $score\n";

  # Return -1 if current score is > $min_score (ie, path is too long)
  if ($score >= min(@$min_score)) {
    debug 3, "--Score too high: $score. End path\n";
    pop(@$visited_cells);
    return -1;
  }

  # Save current score if we've reached the end
  if ($y == scalar(@$map) -1 and $x == scalar(@{$map->[$y]}) -1) {
    debug "Found a path to end with a score of $score\n";
    debug 3, "Path is: ", join("-", @$visited_cells), "\n";
    print_path($map, $visited_cells) if ($DEBUG >= 2);
    push(@$min_score, $score);
    pop(@$visited_cells);
    return $score;
  }

  # Explore nearby cells
  if ($x > 0) {
    find_shortest_path($map, $x-1, $y, $score, $min_score, $visited_cells);
  }
  if ($y > 0) {
    find_shortest_path($map, $x, $y-1, $score, $min_score, $visited_cells);
  }
  if ($x < scalar(@{$map->[$y]}) -1 ) {
    find_shortest_path($map, $x+1, $y, $score, $min_score, $visited_cells);
  }
  if ($y < scalar(@$map) -1 ) {
    find_shortest_path($map, $x, $y+1, $score, $min_score, $visited_cells);
  }

  pop (@$visited_cells);
  return min(@$min_score);
}

############ MAIN ##################


my $file = "input.txt";
while(scalar(@ARGV)) {
  my $arg = pop(@ARGV);
  if (-f $arg) {
    $file = $arg;
  } elsif ($arg eq "-d") {
    $DEBUG++;
  } elsif ($arg eq "-dd") {
    $DEBUG=2;
  } elsif ($arg eq "-ddd") {
    $DEBUG=3;
  }
}
open(FILE, $file) or die("Cannot open file: $file\n");

my $result = 0;
my @map = ();

my $line = 0;
while (<FILE>) {
  debug(3, "Read line: $_");
  chomp;

  @{$map[$line]} = split('', $_);
  $line++;
}

close(FILE);

print_2d_map(\@map);

my @min_score = (9999999999);
my @visited_cells;

$result = find_shortest_path(\@map, 0, 0, 0, \@min_score, \@visited_cells);

debug("\n===================================================================\n");
printf("Result: %d\n", $result);
