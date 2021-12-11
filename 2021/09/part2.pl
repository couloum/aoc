#!/usr/bin/perl -w

use Data::Dumper;
use List::Util qw/min max sum/;

use strict;

sub get_basin_size {
  my ($x, $y, $map) = @_;

  my $max_x = scalar(@$map) - 1;
  my $max_y = scalar(@{$map->[0]}) - 1;

  return 0 if ($x < 0 or $y < 0);
  return 0 if ($x > $max_x or $y > $max_y);
  return 0 if ($map->[$x][$y] == 9);

  # Clear current point
  $map->[$x][$y] = 9;

  # Return size of current position (1) + size of all positions arround
  return 1 
         + get_basin_size($x-1, $y, $map)
         + get_basin_size($x+1, $y, $map)
         + get_basin_size($x, $y-1, $map)
         + get_basin_size($x, $y+1, $map);
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

my @basins_size = ();
for (my $x = 0; $x < scalar(@map); $x++) {
  for (my $y = 0; $y < scalar(@{$map[$x]}); $y++) {
    my $size = get_basin_size($x, $y, \@map);
    printf("In position %d,%d basin size is: %d\n", $x, $y, $size) if ($size > 0);
    push(@basins_size, $size) if ($size > 0);
  }
}

# Get 3 biggest basins
@basins_size = sort({$a <=> $b} @basins_size);
print "All basins: ", join(', ', @basins_size), "\n";
my @big_basins = @basins_size[-3,-2,-1];

print "3 biggest basins' size: ", join(', ', @big_basins), "\n";

my $result = $big_basins[0] * $big_basins[1] * $big_basins[2];
printf("\nResult: %d\n", $result);
