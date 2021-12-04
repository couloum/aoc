#!/usr/bin/perl -w

use Data::Dumper;

use strict;

sub fill_numbers {
  my ($nbr, $cards_ref, $cards_filled_row_ref, $cards_filled_col_ref) = @_;

  # For each card, check if number is present somewhere
  my $cards_win=0;
  foreach my $arrayidx (0..(scalar(@{$cards_ref})-1)) {
    #print "Checking card $arrayidx\n";
    foreach my $rowidx (0..4) {
      foreach my $colidx (0..4) {
          if ($cards_ref->[$arrayidx][$rowidx][$colidx] == $nbr) {
          push @{$cards_filled_row_ref->[$arrayidx][$rowidx]}, $nbr unless $cards_filled_row_ref->[$arrayidx] eq "won";
          push @{$cards_filled_col_ref->[$arrayidx][$colidx]}, $nbr unless $cards_filled_col_ref->[$arrayidx] eq "won";
          $cards_win++;
        }
      }
    }
  }
  print "Number of cards with a match: $cards_win\n";
}

# Check if some cards have 1 row or column filled with 5 numbers and return their numbers
sub get_winning_cards {
  my $cards_filled_row_ref = shift;
  my $cards_filled_col_ref = shift;

  my @winning_cards=();

  foreach my $arrayidx (0..(scalar(@$cards_filled_row_ref)-1)) {
    unless ($cards_filled_row_ref->[$arrayidx] eq "won") {
      foreach my $rowidx (0..4) {
        if (scalar(@{$cards_filled_row_ref->[$arrayidx][$rowidx]}) == 5) {
          push @winning_cards, $arrayidx unless grep /^$arrayidx$/, @winning_cards;
        }
        if (scalar(@{$cards_filled_col_ref->[$arrayidx][$rowidx]}) == 5) {
          push @winning_cards, $arrayidx unless grep /^$arrayidx$/, @winning_cards;
        }
      }
    }
  }
  return @winning_cards;
}

# Calculate summ of all numbers of a card
sub get_sum_numbers {
  my $array_ref = shift;

  my $sum = 0;
  print "0";
  for my $i (0..4) {
    for my $j (0..(scalar(@{$array_ref->[$i]})-1)) {
      my $n = pop @{$array_ref->[$i]};
      $sum += $n;
      print "+$n";
    }
  }
  print "=$sum\n";
  return $sum;
}

# Print a card
sub print_card {
  my $card_ref = shift;
  for my $i (0..4) {
    print join(', ', @{$card_ref->[$i]}), "\n";
  }
}


my $file = "day4-input";
open(FILE, $file) or die("Cannot open file: $file\n");

# Get random numbers
my @randnum = split(/,/, <FILE>);

print "Random numbers: ", join(', ', @randnum), "\n";

# Get carboards
# Each carboard has 5 rows and 5 columns.
# Represent cards with an array of 5 arrays
my @cards;

print "Loading cards\n";
my $arrayidx=0;
while (<FILE>) {
  $_ =~ s/\n$//;

  next if $_ eq "";
  #print "Inserting line in card $arrayidx\n";
  @{$cards[$arrayidx]} = ();

  foreach my $rowidx (0..4) {
    #print "Line: ", $_, "\n";
    @{$cards[$arrayidx][$rowidx]} = split(' ', $_);
    #print "Array: ", @{$cards[$arrayidx][$rowidx]}, "\n";
    #print "$arrayidx/$rowidx: ", join(', ', @{$cards[$arrayidx][$rowidx]}), "\n";

    $_ = <FILE>;
    $_ =~ s/\n$//;
  }
  $arrayidx++;
}
close(FILE);

print scalar(@cards), " cards loaded\n";

# Array for each cards, with number drawns
# One array for rows and one for columns.
my @cards_filled_row;
my @cards_filled_col;

for my $i (0..(scalar(@cards)-1)) {
  @{$cards_filled_row[$i]} = ();
  @{$cards_filled_col[$i]} = ();
  for my $j (0..4) {
    @{$cards_filled_row[$i][$j]} = ();
    @{$cards_filled_col[$i][$j]} = ();
  }
}

print "Drawing random numbers\n";
my $winning_nbr;
my $winning_card;
my $nb_left=scalar(@cards);

# Pull random numbers and check if there's a winner.
# Continue untill there's no more card that hasn't win
foreach my $nbr (@randnum) {
  print "Number pulled: $nbr\n";

  # Check if a row or column is filled
  fill_numbers($nbr, \@cards, \@cards_filled_row, \@cards_filled_col);
  my @winning_cards = get_winning_cards(\@cards_filled_row, \@cards_filled_col);
  if (scalar(@winning_cards) > 0) {
    $nb_left-= scalar(@winning_cards);
    print "Card(s) ", join(', ', @winning_cards), " have win! $nb_left cards still in the game.\n";
    # If there's no more card, we end
    if ($nb_left == 0) {
      $winning_card = @winning_cards[0];
      $winning_nbr = $nbr;
      print "No more cards left. Last winning card: $winning_card. Last drawn number: $winning_nbr\n";
      last;
    } else {
      # Empty the winning cards, so they don't win again
      foreach my $idx (@winning_cards) {
        $cards_filled_col[$idx] = "won";
        $cards_filled_row[$idx] = "won";
      }
    }
  }
}

print "\nThe winning card is $winning_card, with number $winning_nbr.\n";

print_card($cards[$winning_card]);
print "\nRows:\n";
print_card($cards_filled_row[$winning_card]);
print "\nColumns:\n";
print_card($cards_filled_col[$winning_card]);

print "\n";
# Get sum of all numbers, not drawn from winning card:
# Calculate sum of all numbers of the card and subtract numbers drawn

my $sum_card = get_sum_numbers($cards[$winning_card]);
my $sum_drawn = get_sum_numbers($cards_filled_row[$winning_card]);
my $sum_not_drawn = $sum_card - $sum_drawn;

print "sum_card=$sum_card sum_drawn=$sum_drawn sum_not_drawn=$sum_not_drawn\n";


printf("Result: %d\n", $sum_not_drawn * $winning_nbr);
