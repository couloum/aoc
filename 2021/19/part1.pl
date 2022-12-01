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


sub get_beacons_distance{
  my ($scanners) = @_;

  my $beacons_distance = {};

  foreach my $scanner_nb (keys %$scanners) {
    for (my $b1 = 0; $b1 < scalar(@{$scanners->{$scanner_nb}})-1; $b1++) {
      for (my $b2 = $b1+1; $b2 < scalar(@{$scanners->{$scanner_nb}}); $b2++) {
        my ($x1, $y1, $z1) = split(',', $scanners->{$scanner_nb}[$b1]);
        my ($x2, $y2, $z2) = split(',', $scanners->{$scanner_nb}[$b2]);
        my $distance = (abs($x2-$x1) ** 3 + abs($y2-$y1) ** 3 + abs($z2-$z1) ** 3) ** (1/3);
        debug 3, sprintf("Scanner %d, beacons [%d - %d], Distance: [(%d,%d,%d) - (%d,%d,%d)] = %.2f\n", $scanner_nb, $b1, $b2, $x2,$y2,$z2,$x1,$y1,$z1, $distance);
        $beacons_distance->{"$scanner_nb,$b1,$b2"} = sprintf("%.3f", $distance);
      }
    }
  }

  return $beacons_distance;
}

# For each scanner, starting with 0:
#   For each beacon of this scanner:
#     Compare distances with distances of other beacons of other scanners
#     If at least 3 distances are the same, beacon is the same => add it to list of matching beacons
sub get_matching_beacons {
  my ($beacons_distance, $scanners) = @_;

  my $matching_beacons = {};

  for (my $s1 = 0; $s1 < scalar(keys %$scanners) - 1 ; $s1++) {
    for (my $s2 = $s1 + 1; $s2 < scalar(keys %$scanners); $s2++) {
      debug "Evaluating beacons of scanner $s1 with scanner $s2\n";
      for (my $b1 = 0; $b1 < scalar(@{$scanners->{$s1}}); $b1++) {
        debug "  + Evaluating beacon $b1... ";
        my $same_b = compare_beacons($beacons_distance, $scanners, $s1, $b1, $s2);
        if (defined($same_b)) {
          debug "found equivalent beacon: $same_b ($s1,$b1 = $s2,$same_b)\n";
          $matching_beacons->{"$s1,$b1,$s2,$same_b"} = 1;
          $matching_beacons->{"$s2,$same_b,$s1,$b1"} = 1;
        } else {
          debug "no equivalent beacon found\n";
        }
      }
    }
  }
  return $matching_beacons;
}

sub compare_beacons {
  my ($beacons_distance, $scanners, $s1, $b1, $s2) = @_;

  my %b1_distances = ();
  # Get list of disances for s1/b1
  for (my $b2 = 0; $b2 < scalar(@{$scanners->{$s1}}); $b2++) {
    next if ($b1 == $b2);
    $b1_distances{$beacons_distance->{"$s1,$b1,$b2"}} = 1 if (defined $beacons_distance->{"$s1,$b1,$b2"});
    $b1_distances{$beacons_distance->{"$s1,$b2,$b1"}} = 1 if (defined $beacons_distance->{"$s1,$b2,$b1"});
  }

  debug 2, sprintf("(found %d disantes) ", scalar(keys %b1_distances));

  my $matches = {};
  #debug 2, sprintf("[%d", scalar(@{$scanners->{$s2}}));
  for (my $s2b1 = 0; $s2b1 < scalar(@{$scanners->{$s2}}) - 1; $s2b1++) {
    for (my $s2b2 = $s2b1 + 1; $s2b2 < scalar(@{$scanners->{$s2}}); $s2b2++) {
      my $distance = $beacons_distance->{"$s2,$s2b1,$s2b2"};
      debug 3, sprintf("\nchecking if %.2f is in %s\n", $distance, join(', ', keys %b1_distances));
      if (defined($b1_distances{$distance})) {
        $matches->{$s2b1} = 0 if (!defined($matches->{$s2b1}));
        $matches->{$s2b2} = 0 if (!defined($matches->{$s2b2}));
        $matches->{$s2b1}++;
        $matches->{$s2b2}++;
        debug 2, "X";
      } else {
        debug 2, ".";
      }
    } 
  }
  debug 2, " ";

  # Get most matching beacon, with at least 3 beacons

  my $max = 0;
  my $winner;
  foreach my $b (keys %$matches) {
    next if ($matches->{$b} < 3);
    $winner = $b if ($matches->{$b} > $max);
  }

  return $winner;
}

# Recreate a map of all beacons, based on scanners and matching beacons.
# From that map, count total number of beacons
sub count_beacons {
  my ($scanners, $matching_beacons) = @_;

  #
  # Create the map of beacons, relative to scanner 0
  #
  
  my $beacons_map = {};

  # Add all beacons of scanner 0
  foreach my $b (@{$scanners->{0}}) {
    $beacons_map{$b} = "B";
  }

  # Now, identify position of each scanner with scanner 0, based on similar beacons

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

my $scanners = {};
my $cur_scanner = 0;

while (<FILE>) {
  debug(3, "Read line: $_");
  chomp;
  if ($_ =~ /scanner (\d+)/) {
    $scanners->{$1} = [];
    $cur_scanner = $1;
    next;
  } elsif ($_ =~ /^(-?\d+),(-?\d+),(-?\d+)$/) {
    push(@{$scanners->{$cur_scanner}}, "$1,$2,$3");
  }
}

close(FILE);

for (my $cur_scanner = 0; $cur_scanner < scalar(keys %$scanners); $cur_scanner++) {
  debug "--- scanner $cur_scanner ---\n";
  foreach my $beacon (@{$scanners->{$cur_scanner}}) {
    debug 3, "$beacon\n";
  }
  debug sprintf("Beacons found: %d\n", scalar(@{$scanners->{$cur_scanner}}));
}

debug "\n";

# Calculate distance of beacons between each other, for each scanner
my $beacons_distance = get_beacons_distance($scanners);

debug 3,"---------------------------------------\n";
foreach my $key (keys %$beacons_distance) {
  debug 3, sprintf("%s: %.2f\n", $key, $beacons_distance->{$key});
}

debug sprintf("Total of %d distances found\n", scalar(keys %$beacons_distance));
# key = scanner #,beacon 1 #, beacon 2 #
# value = distance = rac(3,abs(x2-x1)^3 + abs(y2-y1)^3  + abs(z2-z1)^3)


# Based on distance, identify similar beacons
my $matching_beacons = get_matching_beacons($beacons_distance, $scanners);

$result = count_beacons($scanners, $matching_beacons);

# Get the total number of beacons

debug("\n===================================================================\n");
printf("Result: %d\n", $result);
