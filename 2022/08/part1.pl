#!/usr/bin/perl -w

use Data::Dumper;
#use List::Util qw/min max/;

use strict;

my $DEBUG = 0;

my $map = {};
my $map_visible = {};


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
my $xmax = scalar(keys %{$map->{0}});
my $ymax = scalar(keys %$map);
debug("Map is $xmax x $ymax size\n");

# Find all "visible" trees.
# Check on the 4 side which tree is visible.

debug(2, "-- Scanning from top to bottom\n");
for (my $x = 0; $x < $xmax; $x++) {
  my $hmax = -1;
  for (my $y = 0; $y < $ymax; $y++) {
    my $h = $map->{$y}->{$x};
    if ($h > $hmax) {
      debug(2, "Visible tree on $x,$y with heigh $h\n");
      $map_visible->{$y}->{$x} = 1;
      $hmax = $h;
    }
  }
}

debug(2, "-- Scanning from left to right\n");
for (my $y = 0; $y < $ymax; $y++) {
  my $hmax = -1;
  for (my $x = 0; $x < $xmax; $x++) {
    my $h = $map->{$y}->{$x};
    if ($h > $hmax) {
      debug(2, "Visible tree on $x,$y with heigh $h\n");
      $map_visible->{$y}->{$x} = 1;
      $hmax = $h;
    }
  }
}

debug(2, "-- Scanning from bottom to top\n");
for (my $x = $xmax-1; $x >= 0; $x--) {
  my $hmax = -1;
  for (my $y = $ymax-1; $y >= 0; $y--) {
    my $h = $map->{$y}->{$x};
    if ($h > $hmax) {
      debug(2, "Visible tree on $x,$y with heigh $h\n");
      $map_visible->{$y}->{$x} = 1;
      $hmax = $h;
    }
  }
}

debug(2, "-- Scanning from right to left\n");
for (my $y = $ymax-1; $y >= 0; $y--) {
  my $hmax = -1;
  for (my $x = $xmax-1; $x >= 0; $x--) {
    my $h = $map->{$y}->{$x};
    if ($h > $hmax) {
      debug(2, "Visible tree on $x,$y with heigh $h\n");
      $map_visible->{$y}->{$x} = 1;
      $hmax = $h;
    }
  }
}

debug("== Map of visible trees\n");
print_2d_map_hash($map_visible);

debug("== Counting visible trees\n");

for (my $x = 0; $x < $xmax; $x++) {
  for (my $y = 0; $y < $ymax; $y++) {
    if ($map_visible->{$y}->{$x}) {
      $result++;
      debug("Found visible tree in $x,$y (total: $result)\n");
    }
  }
}
debug("\n===================================================================\n");
printf("Result: %d\n", $result);
