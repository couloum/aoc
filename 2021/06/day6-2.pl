#!/usr/bin/perl -w

use Data::Dumper;
#use List::Util qw/min max/;
use File::Basename;

use strict;

sub update_lanternfishes {
  my ($lf_ref) = @_;

  # Count number of lf with age 0 that will create a new lf
  my $new_lf = $lf_ref->{0};

  # Decrease age of each lf
  for my $i (1..8) {
    $lf_ref->{$i-1} = $lf_ref->{$i};
  }

  # Create new lf
  $lf_ref->{8} = $new_lf;

  # Set age of 0 lf to 6
  $lf_ref->{6} += $new_lf;
}

sub count_lanternfishes {
  my ($lf_ref) = @_;
  
  my $sum = 0;
  for my $i (0..8) {
    $sum += $lf_ref->{$i};
  }
  return $sum;
}

############ MAIN ##################

my $script = basename($0); 
$script =~ s/.*(day\d+).*/$1/;
my $file = "$script-input";
if (scalar(@ARGV) > 0 and $ARGV[0] eq "sample") {
  $file .= "-sample";
}
open(FILE, $file) or die("Cannot open file: $file\n");

# Create a hash of number of lanternfish per age
my %lanternfishes;

# Init hash
for my $i (0..8) {
  $lanternfishes{$i} = 0;
}

# Fill hash
for my $i (split(/,/, <FILE>)) {
  chomp($i);
  $lanternfishes{$i}++;
}
close(FILE);

my $days = 256;

for my $day (1..$days) {
  update_lanternfishes(\%lanternfishes);
  printf("After %2d days: %d lanternfishes\n", $day, count_lanternfishes(\%lanternfishes));
  #  printf("After %2d days: %s\n", $day, join(',',@lanternfishes));
}

printf("\nResult: %d\n", count_lanternfishes(\%lanternfishes));
