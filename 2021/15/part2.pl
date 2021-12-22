#!/usr/bin/perl -w

use Data::Dumper;
use List::Util qw/min max/;
use List::PriorityQueue;

use strict;

my $DEBUG = 0;

#$|++;

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
      if (defined($visited_cells->{"$x,$y"})) {
        print "\e[31m";
      }
      print $map->[$y][$x];
      print "\e[0m";
    }
    print "\n";
  }
}

sub update_path {
  my ($queue, $nodes_cost, $x, $y, $cost) = @_;

  if (!defined($nodes_cost->{"$x,$y"}) or $cost < $nodes_cost->{"$x,$y"}) {
    $queue->update("$x,$y", $cost);
    $nodes_cost->{"$x,$y"} = $cost;
  }
}

sub visited {
  my ($visited_paths, $x, $y) = @_;

  return defined($visited_paths->{"$x$y"});
}

sub get_max_coord {
  my ($visited_paths) = @_;

  my $max_x = 0;
  my $max_y = 0;
  foreach my $point (keys %$visited_paths) {
    my ($x, $y) = split(',', $point);
    $max_x = max($x, $max_x);
    $max_y = max($y, $max_y);
  }

  return ($max_x, $max_y);
}

# Look at all neighborgh of a point and calculate path
sub scan_neigh {
  my ($map, $x, $y, $visited_paths, $queue, $nodes_cost) = @_;

  my $cur_cost = $nodes_cost->{"$x,$y"};
  my $cost;
  my $point;

  # Compute path of all neighborgh
  update_path($queue, $nodes_cost, $x-1, $y, $cur_cost + $map->[$y][$x-1]) if ($x > 0 and !visited($visited_paths, $x-1, $y));
  update_path($queue, $nodes_cost, $x, $y-1, $cur_cost + $map->[$y-1][$x]) if ($y > 0 and !visited($visited_paths, $y-1, $x));
  update_path($queue, $nodes_cost, $x+1, $y, $cur_cost + $map->[$y][$x+1]) if ($x < scalar(@{$map->[0]}) - 1 and !visited($visited_paths, $x+1,$y));
  update_path($queue, $nodes_cost, $x, $y+1, $cur_cost + $map->[$y+1][$x]) if ($y < scalar(@{$map}) - 1 and !visited($visited_paths, $x, $y+1));

}

sub find_shortest_path {
  my ($map) = @_;

  # Init queue with paths to visit and list of visited paths
  
  my $queue = new List::PriorityQueue;
  my $nodes_cost = {};
  my $visited_paths = {};

  # Start with point 0,0
  $queue->insert("0,0", 0);
  $nodes_cost->{"0,0"} = 0;
  my $max_x = scalar(@{$map->[0]}) -1 ;
  my $max_y = scalar(@$map) - 1;

  my $max_x_visited = 0;
  my $max_y_visited = 0;

  # Loop untill queue is full
  while (1) {
    # Pop point whith shortest path
    my $xy = $queue->pop();
    # Exit if we don't have any item in queue anymore
    if (!defined($xy)) {
      last;
    }
    my ($x, $y) = split(',', $xy);

    #debug 3, "Analyzing point $x,$y - Size of visited_paths: ", scalar(keys %$visited_paths), "\n";

    # Look path to all adjacent cells and add them to the queue or update their cost if not already visited
    scan_neigh($map, $x, $y, $visited_paths, $queue, $nodes_cost);
    
    # Add current point ton visited_paths. We already have its smallest cost in queue
    $visited_paths->{"$x,$y"} = $nodes_cost->{"$x,$y"};

    #my ($tx, $ty) = get_max_coord($visited_paths);
    #if ($tx > $max_x_visited) {
    #  $max_x_visited = $tx;
    #  debug 2, sprintf("New max visited: %d,%d\n", $max_x_visited, $max_y_visited);
    #}
    #if ($ty > $max_y_visited) {
    #  $max_y_visited = $ty;
    #  debug 2, sprintf("New max visited: %d,%d\n", $max_x_visited, $max_y_visited);
    #}
  }

  # Get cost to destination
  return $nodes_cost->{"$max_x,$max_y"};
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

my $size_map = scalar(@map);
# Update map to make it 5 times larger
for (my $i = 1; $i < 5; $i++) {
  for (my $y = 0; $y < $size_map; $y++) {
    my @tmp = ();
    my $y2 = ($i-1)*($size_map) + $y;
    for (my $x = 0; $x < scalar(@{$map[$y]}); $x++) {
      push(@tmp, max(1, ($map[$y2][$x] + 1) % 10));
    }
    push(@map, \@tmp);
  }
}

for (my $y = 0; $y < scalar(@map); $y++) {
  $size_map = scalar(@{$map[$y]});
  for (my $i = 1; $i < 5; $i++) {
    for (my $x = 0; $x < $size_map; $x++) {
      my $x2 = ($i-1)*$size_map + $x;
      push(@{$map[$y]}, max(1, ($map[$y][$x2] + 1) % 10));
    }
  }
}

print_2d_map(\@map) if ($DEBUG >= 3);

$result = find_shortest_path(\@map);

debug("\n===================================================================\n");
printf("Result: %d\n", $result);
