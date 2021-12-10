#!/usr/bin/perl -w

#use Data::Dumper;
#use List::Util qw/min max/;
use File::Basename;

use strict;

sub update_lanternfishes {
  my ($lf_ref) = @_;

  for (my $i = 0; $i < scalar(@$lf_ref); $i++) {
    if ($lf_ref->[$i] == 0) {
      push(@$lf_ref, 9);
      $lf_ref->[$i] = 7;
      #printf("  %d: new fish\n", $i);
    }
    $lf_ref->[$i]--;
  }
}

############ MAIN ##################

my $script = basename($0); 
$script =~ s/.*(day\d+).*/$1/;
my $file = "$script-input";
if (scalar(@ARGV) > 0 and $ARGV[0] == "sample") {
  $file .= "-sample";
}
open(FILE, $file) or die("Cannot open file: $file\n");

chomp(my $line = <FILE>);
my @lanternfishes = split(/,/, $line);
close(FILE);

my $days = 80;

printf("Initial state: %d lanternfishes\n", scalar(@lanternfishes));
#printf("Initial state: %s\n", join(',',@lanternfishes));

for my $day (1..$days) {
  update_lanternfishes(\@lanternfishes);
  printf("After %2d days: %d lanternfishes\n", $day, scalar(@lanternfishes));
#  printf("After %2d days: %s\n", $day, join(',',@lanternfishes));
}

printf("\nResult: %d\n", scalar(@lanternfishes));
