#!/usr/bin/perl -w

use Data::Dumper;
#use List::Util qw/min max/;

use strict;

# Check if octopuses are flashing (energy is > 9).
# In that case, increase energy of adjacent octopuses and see if they flashes
# Return the total number of flashes
sub get_flashes {
  my ($map, $x, $y, $energy_inc) = @_;
  
  return 0 if ($x < 0 or $y < 0);
  return 0 if ($x >= @{$map} or $y >= @{$map->[$x]});
  return 0 if ($map->[$x][$y] < 0);

  # Increment energy if asked (due to previous flash)
  $map->[$x][$y] += $energy_inc;

  my $flashes = 0;
  if ($map->[$x][$y] > 9) {
    # Increment flash counter
    $flashes++;
    # Set current energy to -1 so it cannot flash again
    $map->[$x][$y] = -1;
    # Increase energy of all adjacents octopuses
    # and get total of flashes generated
    for (my $i = -1; $i <= 1; $i++) {
      for (my $j = -1; $j <= 1; $j++) {
        $flashes += get_flashes($map, $x+$i, $y+$j, 1);
      }
    }
  }
  return $flashes;
}

# Make a step in octopuses
# Return 1 if all octopuses have flashed. 0 otherwise.
sub step_octopuses {
  my ($map, $x, $y) = @_;

  # 1 - Increase energy of each octopus by 1
  for (my $x = 0; $x < @{$map}; $x++) {
    for (my $y = 0; $y < @{$map->[$x]}; $y++) {
      $map->[$x][$y]++;
    }
  }

  # 2 - See if some octopuses are flashing
  my $flashes = 0;
  for (my $x = 0; $x < @{$map}; $x++) {
    for (my $y = 0; $y < @{$map->[$x]}; $y++) {
      $flashes += get_flashes($map, $x, $y, 0);
    }
  }

  # At the end of the process, set octopuses with negative energy to 0
  # Check if all octopuses have flashed
  my $flash_flag = 1;
  for (my $x = 0; $x < @{$map}; $x++) {
    for (my $y = 0; $y < @{$map->[$x]}; $y++) {
      $flash_flag = 0 unless ($map->[$x][$y] < 0);
      $map->[$x][$y] = 0 if ($map->[$x][$y] < 0);
    }
  }

  return $flash_flag;

  #printf("Number of flashes: %d\n\n", $flashes);
  #return $flashes;
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

my @octopuses_map = ();
my $x = 0;
while (<FILE>) {
  chomp;
  @{$octopuses_map[$x]} = ();
  foreach my $c (split(//, $_)) {
    push (@{$octopuses_map[$x]}, $c);
  }
  $x++;
}

close(FILE);

print "Before any steps:\n";
print_map(@octopuses_map);
print "\n";

my $steps = 2000;
my $flashes = 0;
my $step = 1;
for ($step = 1; $step <= $steps; $step++) {
  if (step_octopuses(\@octopuses_map)) {
    print "All octopuses have flashed at step $step\n";
    last;
  }
  #  print "After step $step:\n";
  #  print_map(@octopuses_map);
  #  print "\n";
}

print "After all steps:\n";
print_map(@octopuses_map);
print "\n";

printf("\nResult: %d\n", $step);
