#!/usr/bin/perl -w

use Data::Dumper;
#use List::Util qw/min max/;

use strict;

my $DEBUG = 0;

sub debug {
  print @_ if ($DEBUG == 1);
}

sub generate_paths {
  my ($connections) = @_;

  # Create a list of possible paths
  my @paths = ();

  # 1. Generate 1 path per "start" point
  foreach my $connection (keys %$connections) {
    next unless ($connection =~ /start/);
    my ($start, $end) = split('-', $connection);
    my @connection_arr = ();

    if ($start eq "start") {
      push(@connection_arr, $start, $end);
    } else {
      push(@connection_arr, $end, $start);
    }
    push(@paths, \@connection_arr);
    debug(sprintf("%-8s - Creating path\n", $connection));
  }

  # Loop over all possibles paths
  # For each latest end of the path, check if a connection starts or ends with it.
  # If that is the case, checks if next cave is not already present in path if it is a small cave.
  # Ends when we have not added any new cave to any new path.
  #
  my $flag_end = 0;
  while (!$flag_end) {
    debug "Looping over paths\n";
    $flag_end = 1; # Unless told otherwise, we finish the loop

    # Loop over existing paths
    foreach my $path (@paths) {
      debug sprintf("Analyzing path %s\n", join(',', @$path));

      # Get last visited cave in the path
      my $last_cave = $path->[-1];
      my @path_save = ();
      push(@path_save, @$path);

      # Ignore already finished paths
      next if ($last_cave =~ /end$/);
      
      # Loop over connections
      my $duplicate_flag = 0;
      foreach my $connection (keys %$connections) {
        next if ($connection =~ /start/); # ignore paths starting with "start" as we already processed them

        debug sprintf("  * Analyzing connection %s\n", $connection);
        my ($start, $end) = split('-', $connection);

        next if ($start ne $last_cave and $end ne $last_cave); # Ignore if  connection is not related to our current path.
        
        # Determine if connection can be added and in which direction (start->end or end->start)
        
        my ($left, $right);
        if ($last_cave eq $start and ($end =~ /^[A-Z]+$/ or !grep(/^$end$/, @$path))) {
          $left = $start;
          $right = $end;
        } elsif ($last_cave eq $end and ($start =~ /^[A-Z]+$/ or !grep(/^$start$/, @$path))) {
          $left = $end;
          $right = $start;
        } else {
          # In that case, we would go a to small cave we already visited
          next;
        }

        debug sprintf("    - %-8s - Add path %s -> ", $connection, join(',', @path_save));
        if ($duplicate_flag == 0) {
          push(@$path, $right);
          $duplicate_flag = 1;
          debug sprintf("%s\n", join(',', @$path));
        } else {
          # Duplicate the path if we already added a connection to it previously
          my @new_path = @path_save;
          push(@new_path, $right);
          push(@paths, \@new_path);
          debug sprintf("%s\n", join(',', @new_path));
        }
        $flag_end = 0;

      }

    }

    printf("%d paths possibles at the end of the loop\n", scalar(@paths));
  }

  # Remove all dead-end paths: those whose last cave is not "end"
  my @final_paths = ();
  foreach my $path (@paths) {
    push(@final_paths, $path) if (@{$path}[-1] eq "end");
  }

  printf("%d paths possibles after eliminating dead-end paths\n", scalar(@final_paths));
  
  return @final_paths;
}

sub print_paths {
  my ($paths) = @_;

  foreach my $path (@$paths) {
    debug sprintf("%s\n", join(',', @$path));
  }
}

############ MAIN ##################


my $file = "input.txt";
if (scalar(@ARGV) > 0 and -e $ARGV[0]) {
  $file = $ARGV[0];
}
open(FILE, $file) or die("Cannot open file: $file\n");

my %connections = ();

while (<FILE>) {
  chomp;
  $connections{$_} = 1;
}

close(FILE);

my @paths = generate_paths(\%connections);

print_paths(\@paths);
printf("\nResult: %d\n", scalar(@paths));
