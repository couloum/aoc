#!/usr/bin/perl -w

#use Data::Dumper;
#use List::Util qw/min max/;

use strict;

my $DEBUG = 0;


sub print_2d_map {
  my ($map) = @_;

  for (my $y = 0; $y < scalar($map); $y++) {
    for (my $x = 0; $x < scalar($map->[$y]); $x++) {
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

# Find the list of initial X velocities that will permit to reach target.
sub get_x_velocities {
  my ($x1, $x2, $y1, $y2) = @_;

  my $x_range = $x2 - $x1;
  my @valid_x_vel = ();

  for (my $x_vel = 1; $x_vel <= $x2; $x_vel++) {
  
    my $x_vel_cur = $x_vel;
    my $x = 0;

    my $nb_steps = 0;
    my $invalid_flag=0;
    my $step_min;
    my $step_max;

    while($x <= $x2) {
      $x += $x_vel_cur;
      if ($x_vel_cur > 0) {
        $x_vel_cur--;
      } elsif ($x_vel_cur < 0) {
        $x_vel_cur++;
      }
      $nb_steps++;

      # Check if we are in range
      if (!defined($step_min) and $x >= $x1 and $x <= $x2) {
        $step_min = $nb_steps;
      }

      # Check if we have finished
      # 1 - velocity is 0 and we're not in range
      # 2 - velocity is 0 and we're in range
      # 2 - we're above range
      if ($x_vel_cur == 0) {
          if ($x < $x1 or $x > $x2) {
            $invalid_flag = 1;
          }
          last;
      }
    }

    $step_max = $x_vel_cur == 0 ? 500 : $nb_steps - 1;
    # Add the velocity if we hit range
    if (defined($step_min) and !$invalid_flag) {
      push(@valid_x_vel, "$x_vel,$step_min,$step_max");
    }
  }

  debug "Found following valid X velocities: ", join(' - ', @valid_x_vel), "\n";

  return @valid_x_vel;
}

sub get_xy_velocities {
  my ($x1, $x2, $y1, $y2, $x_vel, $step_min, $step_max) = @_;

  debug "Calculating Y velocities matching with X velocity = $x_vel\n";

  my @xy_vel = ();
  for (my $y_vel = $y1; $y_vel < 500; $y_vel++) {

    my $y_vel_cur = $y_vel;
    my $y = 0;

    my $nb_steps = 0;
    my $invalid_flag=1;

    while ($nb_steps < $step_max) {
      $y+=$y_vel_cur;
      $y_vel_cur--;

      $nb_steps++;

      # Check if we are in range and we have enough steps for X
      if ($nb_steps >= $step_min and $y >= $y1 and $y <= $y2) {
        $invalid_flag = 0;
        last;
      }

    }

    if (!$invalid_flag) {
      push(@xy_vel, "$x_vel,$y_vel,$nb_steps");
    }
  }

  debug "Found following valid Y velocities: ", join(' - ', @xy_vel), "\n";

  return @xy_vel;
}

sub get_highest_point {
  my ($y_vel) = @_;

  my $y = 0;
  while ($y_vel > 0) {
    $y += $y_vel;
    $y_vel--;
  }
  return $y;
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

my $line = <FILE>;
chomp $line;
close(FILE);

my ($x1, $x2, $y1, $y2);
if ($line =~ /x=(\d+)..(\d+), y=(-?\d+)..(-?\d+)/) {
  $x1 = $1;
  $x2 = $2; 
  $y1 = $3;
  $y2 = $4;
}

my @x_velocities = get_x_velocities($x1, $x2, $y1, $y2);

my @xy_velocities = ();
foreach my $x_vel_info (@x_velocities) {
  my ($x_vel, $step_min, $step_max) = split(',', $x_vel_info);

  push(@xy_velocities, get_xy_velocities($x1, $x2, $y1, $y2, $x_vel, $step_min, $step_max));
}

$result = scalar(@xy_velocities);

debug("\n===================================================================\n");
printf("Result: %d\n", $result);
