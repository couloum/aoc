#!/usr/bin/perl -w

use Data::Dumper;
#use List::Util qw/min max/;

use strict;

# Return true if digit in 1st parameter has a lower value than all values
# in the array in 2nd parameter
sub is_low_point {
  my ($point, $next_values) = @_;

  for my $v (@$next_values) {
    return 0 if ($point >= $v);
  }
  print "$point is lower than ", join(', ', @$next_values), "\n";
  return 1;
}

# Return the coordonate (x,y) of low points in the map
# provided as a 2-dimensionnal array
sub get_low_point_coordonates {
  my @map = @_;

  my $max_x = scalar(@map);
  my $max_y = scalar(@{$map[0]});

  my @low_point_coordonates = ();

  for (my $x = 0; $x < $max_x; $x++) {
    for (my $y = 0; $y < $max_y; $y++) {
      # Get value of points next to the one we are cheking
      my @next_values = ();
      push(@next_values, $map[$x-1][$y]) if ($x > 0);
      push(@next_values, $map[$x+1][$y]) if ($x < $max_x - 1);
      push(@next_values, $map[$x][$y-1]) if ($y > 0);
      push(@next_values, $map[$x][$y+1]) if ($y < $max_y - 1);
      
      # Check if current point is low point
      push(@low_point_coordonates, "$x,$y") if (is_low_point($map[$x][$y], \@next_values));
    }
  }
  return @low_point_coordonates;
}

# Just for debugging
# Print the full map
sub print_map {
  my @map = @_;
  for (my $x = 0; $x < scalar(@map); $x++) {
    for (my $y = 0; $y < scalar(@{$map[$x]}); $y++) {
      print $map[$x][$y];
    }
    print "\n";
  }
}
############ MAIN ##################

my $file = "input.txt";
if (scalar(@ARGV) > 0 and -e $ARGV[0]) {
  $file = $ARGV[0];
}
open(FILE, $file) or die("Cannot open file: $file\n");

my @map = ();
my $x = 0;
while (<FILE>) {
  chomp;
  push(@map, ());
  foreach my $c (split('', $_)) {
    push(@{$map[$x]}, $c);
  }
  $x++;
}

close(FILE);

#print_map(@map);

my @low_points_coordonates = get_low_point_coordonates(@map);

my $sum = 0;
for my $point (@low_points_coordonates) {
  my ($x, $y) = split(',', $point);
  printf("Point at location %d,%d is %d\n", $x, $y, $map[$x][$y]);
  $sum += $map[$x][$y] + 1;
}

printf("\nResult: %d\n", $sum);
