#!/usr/bin/perl -w

#use Data::Dumper;
#use List::Util qw/min max/;

use strict;

my $DEBUG = 0;


$|++;
sub print_2d_map {
  my ($map) = @_;

  for (my $y = 0; $y < scalar(@$map); $y++) {
    printf "%3s: ", $y;
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

sub fold_y {
  my ($map, $point) = @_;

  debug 1, sprintf("Map size is %d, folding on %d\n", scalar(@$map), $point);
  for (my $y = 0 ; $y <= $point; $y++) {
    my $y2 = scalar(@$map) - 1;
    debug 3, "Replicating points from $y2 on $y\n";
    foreach (my $x = 0; $x < scalar(@{$map->[$y2]}); $x++) {
      $map->[$y][$x] = '#' if ($map->[$y2][$x] eq '#');
      debug 3, $map->[$y][$x];
    }
    delete($map->[$y2]);
    debug 3, "\n";
  }
}

sub fold_x {
  my ($map, $point) = @_;

  debug 1, sprintf("Map size is %d, folding on %d\n", scalar(@{$map->[0]}), $point);
  for (my $x = 0 ; $x <= $point; $x++) {
    for (my $y = 0; $y < scalar(@$map); $y++) {
      my $x2 = scalar(@{$map->[$y]}) - 1;
      $map->[$y][$x] = '#' if ($map->[$y][$x2] eq '#');
      delete($map->[$y][$x2]);
    }
  }
}

sub apply_folds {
  my ($map, $folds) = @_;

  foreach my $fold (@$folds) {
    my ($dir, $point) = split('=', $fold); 
    debug "Folding on $fold\n";
    fold_y($map, $point) if ($dir eq 'y');
    fold_x($map, $point) if ($dir eq 'x');
  }
}

sub count_dots {
  my ($map) = @_;

  my $nb = 0;
  for (my $y = 0; $y < scalar(@$map); $y++) {
    for (my $x = 0; $x < scalar(@{$map->[$y]}); $x++) {
      $nb++ if ($map->[$y][$x] eq "#");
    }
  }
  return $nb;
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

my $max_x = 0;
my $max_y = 0;

my @points = ();
my @folds = ();
while (<FILE>) {
  debug(3, "Read line: $_");

  chomp;
  if ($_ =~ /^(\d+),(\d+)$/) {
    push (@points, "$1,$2");
  } elsif ($_ =~ /fold along ([xy])=(\d+)$/) {
    push(@folds, "$1=$2");
    $max_x = $2*2 if ($1 eq "x" and $2*2 > $max_x);
    $max_y = $2*2 if ($1 eq "y" and $2*2 > $max_y);
  }
}

close(FILE);

debug "max X: $max_x / max Y: $max_y\n";

# Init map
for (my $y = 0; $y <= $max_y; $y++) {
  my @row = ();
  for (my $x = 0; $x <= $max_x; $x++) {
    push(@row, '.');
  }
  @{$map[$y]} = @row;
}

# Insert points
for my $point (@points) {
  my ($x, $y) = split(',', $point);
  $map[$y][$x] = '#';
}

print_2d_map(\@map) if ($DEBUG == 3);

apply_folds(\@map, \@folds);

debug("\n===================================================================\n");
print "Result:\n";
print_2d_map(\@map);
