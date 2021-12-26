#!/usr/bin/perl -w

#use Data::Dumper;
use List::Util qw/min max/;
use POSIX qw/ceil floor/;

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

# Perform explode and split operations on the number:
# To reduce a snailfish number, you must repeatedly do the first action in this
# list that applies to the snailfish number:
# - If any pair is nested inside four pairs, the leftmost such pair explodes.
# - If any regular number is 10 or greater, the leftmost such regular number splits.
#
# To explode a pair, the pair's left value is added to the first regular number
# to the left of the exploding pair (if any), and the pair's right value is
# added to the first regular number to the right of the exploding pair (if
# any). Exploding pairs will always consist of two regular numbers. Then, the
# entire exploding pair is replaced with the regular number 0.
#
# To split a regular number, replace it with a pair; the left element of the
# pair should be the regular number divided by two and rounded down, while the
# right element of the pair should be the regular number divided by two and
# rounded up. For example, 10 becomes [5,5], 11 becomes [5,6], 12 becomes
# [6,6], and so on.

sub reduce {
  my ($number) = @_;

  debug sprintf("%-20s: %s\n", "Reducing number", $number);

  my $flag = 1;
  while ($flag) {
    $flag = 0;
    my $new_number = do_explode($number);
    if ($new_number ne $number) {
      $number = $new_number;
      $flag = 1;
      next;
    } else {
      $new_number = do_split($number);
      if ($new_number ne $number) {
        $number = $new_number;
        $flag = 1;
        next;
      }
    }
  }

  return $number;
}

sub num_to_arr {
  my ($number) = @_;

  my @num = ();
  for (my $i = 0; $i < length($number); $i++) {
    my $c = substr($number, $i, 1);
    if ($c =~ /[\[\],]/) {
      push(@num, $c);
      next;
    }

    # Check if tis si a single digit or doucle digit number
    my $c2 = substr($number, $i+1, 1);
    if ($c2 =~ /\d/) {
      my $val = $c*10 + $c2;
      push(@num, $val);
      $i++;
    } else {
      push(@num, $c);
    }
  }

  return @num;
}

sub do_explode {
  my ($number) = @_;

  my $level = 0;

  debug 2, sprintf("%-20s: %s\n", "Explode number", $number);

  # Convert number in array
  my @num = num_to_arr($number);

  for (my $i = 0; $i < scalar(@num); $i++) {
    my $c = $num[$i];
    #debug 3, "[$level] Reading char $c\n";

    if ($c eq '[') {
      $level++;
    } elsif ($c eq ']') {
      $level--;
    }
    # Try to split first
    if ($level > 4 and $c =~ /^\d+$/) {
      # Check that right part of the pair is a number
      my $c2 = $num[$i+2];
      if ($c2 eq '[') {
        # Right part is another part. Skip to this pair
        $i++;
        next;
      }

      # Get left and right values
      my $left_val = $num[$i];
      my $right_val = $num[$i+2];

      # Delete current pair from array and replace it with a 0
      @num[$i-1] = 0;
      splice(@num, $i, 4);

      debug 3, sprintf("%-20s: %s\n", "DEBUG (+$left_val,+$right_val)", join('', @num));

      # Add left value with first regular number on left
      for (my $j = $i-2; $j >= 0 ; $j--) {
        if ($num[$j] =~ /^\d+$/) {
          # Check if that number is a double digit number
          $num[$j]+=$left_val;
          last;
        }
      }
      # Add right value with first regular number on right
      for (my $j = $i+1; $j < scalar(@num); $j++) {
        if ($num[$j] =~ /^\d+$/) {
          $num[$j]+=$right_val;
          last;
        }
      }

      $number = join('', @num);

      debug 2, sprintf("%-20s: %s\n", "New number", $number);

      # Return the new number
      return join('', @num);
    }
  }

  debug 2, "No explode done\n";
  return $number;
}

sub do_split {
  my ($number) = @_;

  debug 2, sprintf("%-20s: %s\n", "Split number", $number);
  # Check if there is pairs with 2 digits in the number
  if ($number =~ /(\d\d)/) {
    my $val = $1;

    # get position of that number
    my $i = index($number, $val);

    my $new_number = substr($number, 0, $i);

    $new_number .= sprintf("[%d,%d]", floor($val/2), ceil($val/2));
    $new_number .= substr($number, $i+2);

    debug 2, sprintf("%-20s: %s\n", "New number", $new_number);

    return $new_number;

  }
  
  debug 2, "No split done\n";
  return $number;
}

sub get_magnitude {
  my ($number) = @_;

  my @num = num_to_arr($number);

  for (my $i = 0; $i < scalar(@num); $i++) {
    if ($num[$i] eq ']') {
      # The magnitude of a pair is 3 times the magnitude of its left element plus 2 times the magnitude of its right element
      my $mag = $num[$i-3] * 3 + $num[$i-1] * 2;
      # Replace pair with magnitude
      splice(@num, $i-4, 5, $mag);
      $i -= 4;
    }
  }
  return $num[0];
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

my $number;

while (<FILE>) {
  debug(3, "Read line: $_");
  chomp;

  if (!defined($number)) {
    $number = $_;
  } else {
    # Add new number with previous result
    $number = "[$number,$_]";
  }

  $number = reduce($number);
}

close(FILE);

debug "Number after reduce: $number\n";

$result = get_magnitude($number);

debug("\n===================================================================\n");
printf("Result: %s\n", $result);
