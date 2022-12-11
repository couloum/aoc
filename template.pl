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

while (<FILE>) {
  debug(3, "Read line: $_");
  chomp;
}

close(FILE);

debug("\n===================================================================\n");
printf("Result: %d\n", $result);
