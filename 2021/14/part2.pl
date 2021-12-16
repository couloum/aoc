#!/usr/bin/perl -w

use Data::Dumper;
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



############ FUNCTIONS #############

sub get_polymer_from_str {
  my ($str) = @_;

  my %polymer = ();

  for (my $i= 0; $i < length($str) - 1; $i++) {
    my $pair = substr($str, $i, 2);
    $polymer{$pair} = 0 if (!defined($pair));
    $polymer{$pair}++;
  }

  return %polymer;
}

sub polymerization {
  my ($polymer, $rules, $steps) = @_;

  for (my $step = 0; $step < $steps; $step++) {
    debug "### STEP $step ###\n";

    my %polymer_backup = %$polymer;

    for my $pair (sort keys %polymer_backup) {
      # Skip empty pairs
      next unless ($polymer_backup{$pair} > 0);

      debug 3, "Analyzing pair <$pair>";
      if (defined($rules->{$pair})) {
        my ($l1, $l2, $l3) = split('', $rules->{$pair});
        my ($p1, $p2) = ("$l1$l2", "$l2$l3");
        #debug 3, " (", $rules->{$pair}, ") - Transforming into <$p1> <$p2>";
        debug 3, sprintf(" (%d) --> <%s> (%d) <%s> (%d) ", $polymer->{$pair}, $p1, $polymer->{$p1}, $p2, $polymer->{$p2});
        my $nb_pairs = $polymer_backup{$pair};
        $polymer->{$pair}-= $nb_pairs;
        $polymer->{$p1} = 0 if (!defined($polymer->{$p1}));
        $polymer->{$p2} = 0 if (!defined($polymer->{$p2}));
        $polymer->{$p1}+=$nb_pairs;
        $polymer->{$p2}+=$nb_pairs;
        debug 3, sprintf("| <%s> (%d) --> <%s> (%d) <%s> (%d)", $pair, $polymer->{$pair}, $p1, $polymer->{$p1}, $p2, $polymer->{$p2});
      } else {
        debug "Error: pair <$pair> does not exist\n";
      }
      debug 3, "\n";
    }

    #debug 3, Dumper %$polymer;
    debug "Number of pairs in the polymer:", get_nb_pairs($polymer), "\n";
    debug 2, "Polymer stats: ", join(' - ', get_polymer_stats($polymer)), "\n";
  }

  return $polymer;
}

sub get_min_max_letter {
  my ($polymer, $last_letter) = @_;

  # Calculate number of letters
  my %letters = ();

  for my $pair (keys %$polymer) {
    my ($l1, $l2) = split('', $pair);

    $letters{$l1} = 0 if(!defined($letters{$l1}));
    $letters{$l1} += $polymer->{$pair};
  }

  $letters{$last_letter}++;

  my $min_l;
  my $min = 9999999999999;
  my $max_l;
  my $max = 0;

  for my $l (keys %letters) {
    if ($letters{$l} < $min) {
      $min = $letters{$l};
      $min_l=$l;
    }
    if ($letters{$l} > $max) {
      $max = $letters{$l};
      $max_l=$l;
    }
  }

  return ($min_l, $min, $max_l, $max);
}

sub get_nb_pairs {
  my ($polymer) = @_;

  my $nb =0;
  foreach my $pair (keys %$polymer) {
    $nb += $polymer->{$pair};
  }

  return $nb;
}

sub get_polymer_stats {
  my ($polymer) = @_;
  my @stats = ();
  foreach my $pair (sort keys %$polymer) {
    push(@stats, sprintf("<%s> (%d)", $pair, $polymer->{$pair})) if ($polymer->{$pair} > 0);
  }
  return @stats;
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

my $polymer_str = <FILE>;
chomp $polymer_str;

my %polymer = get_polymer_from_str($polymer_str);

debug sprintf("Polymer: %s\n", $polymer_str);

<FILE>;

my %rules = ();

while (<FILE>) {
  debug(3, "Read line: $_");
  chomp;
  if ($_ =~ /^(.)(.) -> (.)$/) {
    $rules{"$1$2"} = "$1$3$2";
  }
}

close(FILE);

my $polymer_result = polymerization(\%polymer, \%rules, 40);

debug "Polymer stats: ", join(' - ', get_polymer_stats($polymer_result)), "\n";

# get min/max used letter
my ($min_l, $min, $max_l, $max) = get_min_max_letter($polymer_result, substr($polymer_str, length($polymer_str)-1, 1));

debug sprintf("Min letter: %s (%d) / Max letter: %s (%d)\n", $min_l, $min, $max_l, $max);

$result = $max - $min;

debug("\n===================================================================\n");
printf("Result: %d\n", $result);
