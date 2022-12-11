#!/usr/bin/perl -w

use Data::Dumper;
#use List::Util qw/min max/;

use strict;

my $DEBUG = 0;

my $map = {};
my $map_visible = {};
my $xmax = 0;
my $ymax = 0;


sub print_2d_map {
  my ($map) = @_;

  for (my $y = 0; $y < scalar(@$map); $y++) {
    for (my $x = 0; $x < scalar(@{$map->[$y]}); $x++) {
      print $map->[$y][$x];
    }
    print "\n";
  }
}

sub print_2d_map_hash {
  my $map = shift;

  for (my $y = 0; $y < scalar(keys %$map); $y++) {
    for (my $x = 0; $x < scalar(keys %{$map->{$y}}); $x++) {
      print $map->{$y}->{$x};
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

sub get_scenic_score {
  my ($cx, $cy) = @_;
  my ($x, $y) = ($cx, $cy);

  debug(2, "-- Scanning from top to bottom\n");

  my $hmax = $map->{$y}->{$x};
  my ($left, $right, $top, $botom)  = (0, 0, 0, 0);
  my $bottom = 0;
  
  # Get "bottom" (check from top to bottom)
  if ($cy < $ymax - 1) {
    $x = $cx;
    my $distance = 0;
    for (my $y = $cy + 1; $y < $ymax; $y++) {
      my $h = $map->{$y}->{$x};
      $distance++;
      if ($h >= $hmax) {
        last;
      }
    }
    $bottom = $distance;
  }

  # Get "right" (check from left to right)
  if ($cx < $xmax - 1) {
    $y = $cy;
    my $distance = 0;
    for (my $x = $cx+1; $x < $xmax; $x++) {
      my $h = $map->{$y}->{$x};
      $distance++;
      if ($h >= $hmax) {
        last;
      }
    }
    $right = $distance;
  }

  # Get "top" (check from bottom to top)
  if ($cy > 0) {
    $x = $cx;
    my $distance = 0;
    for (my $y = $cy-1; $y >= 0; $y--) {
      my $h = $map->{$y}->{$x};
      $distance++;
      if ($h >= $hmax) {
        last;
      }
    }
    $top = $distance;
  }

  # Get "left" (check from right to left)
  if ($cx > 0) {
    $y = $cy;
    my $distance = 0;
    for (my $x = $cx-1; $x >= 0; $x--) {
      my $h = $map->{$y}->{$x};
      $distance++;
      if ($h >= $hmax) {
        last;
      }
    }
    $left = $distance;
  }

  return $top * $bottom * $left * $right;
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

# Get map of tress
my $y = 0;
while (my $line = <FILE>) {
  debug(3, "Read line: $line");
  chomp $line;
  my $x = 0;
  $map->{$y} = {};
  $map_visible->{$y} = {};
  foreach my $str (split(//, $line)) {
    $map->{$y}->{$x} = $str;
    $map_visible->{$y}->{$x} = 0;
    $x++;
  }
  $y++;
}

close(FILE);

#print Dumper $map;
$xmax = scalar(keys %{$map->{0}});
$ymax = scalar(keys %$map);
debug("Map is $xmax x $ymax size\n");

# Find all "visible" trees.
# Check on the 4 side which tree is visible.

my $max_scenic_score = 0;

for (my $x = 0; $x < $xmax; $x++) {
  for (my $y = 0; $y < $ymax; $y++) {
    my $scenic_score = get_scenic_score($x, $y);
    if ($scenic_score > $max_scenic_score) {
      $max_scenic_score = $scenic_score;
      debug("New max scenic score in $x,$y: $scenic_score\n");
    }
  }
}

$result = $max_scenic_score;
debug("\n===================================================================\n");
printf("Result: %d\n", $result);
