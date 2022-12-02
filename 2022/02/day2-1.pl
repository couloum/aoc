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

sub get_shape_point {
  my $shape = shift;

  my $ret = 3;
  $ret = 1 if ($shape =~ /[AX]/);
  $ret = 2 if ($shape =~ /[BY]/);

  debug(3, "shape points: $shape -> $ret\n");

  return $ret;
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

my $total_score = 0;

while (<FILE>) {
  debug(3, "Read line: $_");
  chomp;

  # A = Rock
  # B = Paper
  # C = Scissors
  # X = Rock
  # Y = Paper
  # Z = Scissors
  if ($_ =~ /^([ABC]) ([XYZ])/) {
    my $a = $1;
    my $b = $2;

    my $elves_score = 0;
    my $my_score = 0;

    # Calculate who win?
    if ("$a$b" =~ /(AX|BY|CZ)/) { # Draw
      $elves_score = 3;
      $my_score = 3;
    } elsif ("$a$b" =~ /(AY|BZ|CX)/) { # I win
      $my_score = 6;
    } else {
      $elves_score = 6;
    }

    debug(3, "$a $b || $elves_score $my_score\n");

    # Add points for shape played
    $elves_score += get_shape_point($a);
    $my_score += get_shape_point($b);


    # Add my score to my total score
    $total_score += $my_score;
    debug("$a $b || $elves_score $my_score || $total_score\n");

  }
}

close(FILE);

$result = $total_score;
debug("\n===================================================================\n");
printf("Result: %d\n", $result);
