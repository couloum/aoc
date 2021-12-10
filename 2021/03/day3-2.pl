#!/usr/bin/perl -w

use strict;

my $file = "day3-input";
open(FILE, $file) or die("Cannot open file: $file\n");

sub str2dec {
  my $str = shift;
  #print "Converting $str in decimal: ";
  my $nbr = 0;
  my $size = length($str) - 1;
  for my $i (0..$size) {
    $nbr <<= 1;
    $nbr+=substr($str, $i, 1);
    #print "  $i: $nbr\n";
  }
  #print "$nbr\n";

  return $nbr;
}

sub get_most_present_digit {
  my ($pos, @numbers) = @_;

  my $nb0 = 0;
  my $nb1 = 0;
  for my $nbr (@numbers) {
    $nb0++ if substr($nbr, $pos, 1) == "0";
    $nb1++ if substr($nbr, $pos, 1) == "1";
  }

  return 0 if $nb0 > $nb1;
  return 1;
}

sub filter_numbers {
  my ($filter, $pos, @numbers) = @_;

  my @tmp;

  for my $nbr (@numbers) {
    push @tmp, $nbr if substr($nbr, $pos, 1) == $filter;
  }

  return @tmp;
}

my @numbers=();


# Keep numbers in memory
while (<FILE>) {
  $_ =~ s/\n$//;

  push @numbers, $_;
}

close($file);

my @oxygen_numbers = @numbers;
my @co2_numbers = @numbers;

# Find Oxygen
for my $i (0..11) {
  print "Loop $i/11:\n"; 

  print "  Size of \@oxygen_numbers before: ", scalar(@oxygen_numbers), "\n";
  print "  Size of \@co2_numbers before:    ", scalar(@co2_numbers), "\n";

  # Find most and less common digit on that position
  my $oxy_digit=get_most_present_digit($i, @oxygen_numbers);

  my $co2_digit=get_most_present_digit($i, @co2_numbers);
  # Reverse value of co2_digit
  $co2_digit=($co2_digit + 1) % 2;

  print "  Most common digit in \@oxygen_numbers: $oxy_digit\n";
  print "  Less common digit in \@co2_numbers:    $co2_digit\n";

  # Now continue filtering digits if still more than 1 number after previous filtering

  if (@oxygen_numbers > 1) {
    @oxygen_numbers = filter_numbers($oxy_digit, $i, @oxygen_numbers);
  }
  if (@co2_numbers > 1) {
    @co2_numbers = filter_numbers($co2_digit, $i, @co2_numbers);
  }

  print "  Size of \@oxygen_numbers after: ", scalar(@oxygen_numbers), "\n";
  print "  Size of \@co2_numbers after:    ", scalar(@co2_numbers), "\n";
}

my $d_oxy = str2dec($oxygen_numbers[0]);
my $d_co2 = str2dec($co2_numbers[0]);

printf("\nResult: %d [oxy=%s (%d) co2=%s (%d)]\n", $d_oxy*$d_co2, $oxygen_numbers[0], $d_oxy, $co2_numbers[0], $d_co2);
