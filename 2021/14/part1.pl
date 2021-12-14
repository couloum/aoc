#!/usr/bin/perl -w

#use Data::Dumper;
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

  my @polymer = ();

  for (my $i= 0; $i < length($str) - 1; $i++) {
    push(@polymer, substr($str, $i, 2));
  }

  return @polymer;
}

sub polymerization {
  my ($polymer, $rules, $steps) = @_;

  for (my $step = 0; $step < $steps; $step++) {
    debug "### STEP $step ###\n";

    my @tmp_polymer = ();
    for my $pair (@$polymer) {
      debug 3, "Analyzing pair <$pair>";
      if (defined($rules->{$pair})) {
        my ($p1, $p2, $p3) = split('', $rules->{$pair});
        debug 3, " (", $rules->{$pair}, ") - Transforming into <$p1$p2> <$p2$p3>";
        push(@tmp_polymer, "$p1$p2");
        push(@tmp_polymer, "$p2$p3");
      }
      debug 3, "\n";
    }

    $polymer = \@tmp_polymer;
  }

  return $polymer;
}

sub get_polymer_from_array {
  my ($arr) = @_;

  my $polymer = "";

  for my $pair (@$arr) {
    $polymer .= substr($pair, 0, 1);
  }
  $polymer .= substr($arr->[-1], 1, 1);

  return $polymer;
}

# From a given polymer, as string, get the total number of letters, per letter
sub get_letters_qty {
  my ($polymer) = @_;

  my %qty = ();
  for (my $i = 0; $i < length($polymer); $i++) {
    my $l = substr($polymer, $i, 1);
    $qty{$l} = 0 if (!defined($qty{$l}));
    $qty{$l}++;
  }

  return %qty;
}

sub get_min_max_letter {
  my (%qty) = @_;

  my $min_l;
  my $min = 999999;
  my $max_l;
  my $max = 0;

  for my $l (keys %qty) {
    if ($qty{$l} < $min) {
      $min = $qty{$l};
      $min_l=$l;
    }
    if ($qty{$l} > $max) {
      $max = $qty{$l};
      $max_l=$l;
    }
  }

  return ($min_l, $min, $max_l, $max);
}

############ MAIN ##################


my $file = "input.txt";
while(scalar(@ARGV)) {
  my $arg = pop(@ARGV);
  if (-f $arg) {
    $file = $arg;
  }
  if ($arg eq "-d") {
    $DEBUG++;
  }
}
open(FILE, $file) or die("Cannot open file: $file\n");

my $result = 0;

my $polymer_str = <FILE>;
chomp $polymer_str;

my @polymer = get_polymer_from_str($polymer_str);

debug sprintf("Polymer: %s\n", $polymer_str);
debug 3, sprintf("Polymer in array: %s\n", join(', ', @polymer));

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

my $polymer_result = polymerization(\@polymer, \%rules, 10);
$polymer_str = get_polymer_from_array($polymer_result);

debug 3, sprintf("Polymer in array: %s\n", join(', ', @$polymer_result));
debug 2, sprintf("New polymer: %s\n", $polymer_str);

my %qty = get_letters_qty($polymer_str);

# get min/max used letter
my ($min_l, $min, $max_l, $max) = get_min_max_letter(%qty);

$result = $max - $min;

debug("\n===================================================================\n");
printf("Result: %d\n", $result);
