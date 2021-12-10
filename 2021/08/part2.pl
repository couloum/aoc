#!/usr/bin/perl -w

#use Data::Dumper;
#use List::Util qw/min max/;

use strict;

sub sort_str {
  my ($str) = @_;
  return join('', sort(split(//, $str)));
}

sub str_in_str {
  my ($search, $str) = @_;

  foreach my $c (split(//, $search)) {
    return 0 if (index($str, $c) == -1);
  }
  return 1;
}

sub nb_letters_diff {
  my ($a, $b) = @_;
  my $big;
  my $small;
  my $diff = 0;

  if (length($a) >= length($b)) {
    $big = $a;
    $small = $b;
  } else {
    $big = $b;
    $small = $a;
  }

  foreach my $c (split(//, $big)) {
    $diff++ if (index($small, $c) == -1);
  }
  return $diff;
}

#0: abc efg
#1:   c  f
#2: a cde g
#3: a cd fg
#4:  bcd f
#5: ab d fg
#6: ab defg
#7: a c  f
#8: abcdefg
#9: abcd fg
#
#1:   c  f
#4:  bcd f
#7: a c  f
#
#0 = 6 /  1 !4  7
#2 = 5 / !1 !4 !7
#3 = 5 /  1 !4  7
#5 = 5 / !1 !4 !7
#6 = 6 / !1 !4 !7
#9 = 6 /  1  4  7

sub decode_line {
  my ($line) = @_;

  my $signal = $line;
  $signal =~ s/ \|.*//;

  my @digits = split(' ', $signal);

  my %codex = (
    'abcdefg' => 8,
  );
  my %r_codex = (
    8 => 'abcdefg',
  );

  # Stage 1, identify 1, 4, 7
  foreach my $digit (@digits) {
    my $sorted_digit = sort_str($digit);

    if (!defined($r_codex{1}) and length($digit) == 2) {
      $r_codex{1} = $sorted_digit;
      $codex{$sorted_digit} = 1;
    } elsif (!defined($r_codex{7}) and length($digit) == 3) {
      $r_codex{7} = $sorted_digit;
      $codex{$sorted_digit} = 7;
    } elsif (!defined($r_codex{4}) and length($digit) == 4) {
      $r_codex{4} = $sorted_digit; 
      $codex{$sorted_digit} = 4;
    }
    # Exit if we found the 4 digits
    if (scalar(keys(%r_codex)) == 4) {
      last;
    }
  }
  if (!scalar(keys(%r_codex)) == 4) {
    die("Error: we couldn't find the 4 digits in line $line\n");
  }

  # Stage 2, identify 0, 3, 6 and 9
  foreach my $digit (@digits) {
    my $sorted_digit = sort_str($digit);
    if (length($digit) == 6) {
      if ( 
          !defined($r_codex{0}) and
           str_in_str($r_codex{1}, $sorted_digit) and
          !str_in_str($r_codex{4}, $sorted_digit) and
           str_in_str($r_codex{7}, $sorted_digit)
         ) {
         $r_codex{0} = $sorted_digit;
         $codex{$sorted_digit} = 0;
      } elsif (
          !defined($r_codex{6}) and
          !str_in_str($r_codex{1}, $sorted_digit) and
          !str_in_str($r_codex{4}, $sorted_digit) and
          !str_in_str($r_codex{7}, $sorted_digit)
         ) {
         $r_codex{6} = $sorted_digit;
         $codex{$sorted_digit} = 6;
      } elsif (
          !defined($r_codex{9}) and
           str_in_str($r_codex{1}, $sorted_digit) and
           str_in_str($r_codex{4}, $sorted_digit) and
           str_in_str($r_codex{7}, $sorted_digit)
         ) {
         $r_codex{9} = $sorted_digit;
         $codex{$sorted_digit} = 9;
      }
    
      if (scalar(keys(%r_codex)) == 7) {
        last;
      }
    }
  }
  if (!scalar(keys(%r_codex)) == 7) {
    die("Error: we couldn't find the 7 digits in line $line\n");
  }

  # Stage 3, identify 2, 3 and 5
  foreach my $digit (@digits) {
    my $sorted_digit = sort_str($digit);
    if (length($digit) == 5) {
      if ( 
          !defined($r_codex{3}) and
           str_in_str($r_codex{1}, $sorted_digit) and
          !str_in_str($r_codex{4}, $sorted_digit) and
           str_in_str($r_codex{7}, $sorted_digit)
         ) {
         $r_codex{3} = $sorted_digit;
         $codex{$sorted_digit} = 3;
      } elsif (
          !defined($r_codex{2}) and
          nb_letters_diff($r_codex{9}, $sorted_digit) == 2
         ) {
         $r_codex{2} = $sorted_digit;
         $codex{$sorted_digit} = 2;
      } elsif (
          !defined($r_codex{5}) and
          nb_letters_diff($r_codex{9}, $sorted_digit) == 1
         ) {
         $r_codex{5} = $sorted_digit;
         $codex{$sorted_digit} = 5;
      }
    
      if (scalar(keys(%r_codex)) == 10) {
        last;
      }
    }
  }
  if (!scalar(keys(%r_codex)) == 10) {
    die("Error: we couldn't find the 10 digits in line $line\n");
  }
  
  return \%codex;
}

sub decode_output {
  my ($line, $codex) = @_;

  my $result = "";
  if ($line =~ /\| (.*)/) {
    my @output = split(' ', $1);
    foreach my $digit (@output) {
      my $sorted_digit = sort_str($digit);
      $result .= $codex->{$sorted_digit};
    }
  }

  return $result;
}
############ MAIN ##################

my $file = "input.txt";
if (scalar(@ARGV) > 0 and -e $ARGV[0]) {
  $file = $ARGV[0];
}
open(FILE, $file) or die("Cannot open file: $file\n");

my $sum_output = 0;
while (<FILE>) {
  chomp;
  my $codex = decode_line($_);
  my $output = decode_output($_, $codex);
  print "$output\n";
  $sum_output += $output;
}

close(FILE);


printf("\nResult: %d\n", $sum_output);
