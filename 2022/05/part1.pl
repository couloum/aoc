#!/usr/bin/perl -w

use Data::Dumper;
#use List::Util qw/min max/;

use strict;

my $DEBUG = 0;

my @stacks = ();
my $nb_stacks = 0;


sub print_2d_map {
  my ($map) = @_;

  for (my $y = 0; $y < scalar(@$map); $y++) {
    for (my $x = 0; $x < scalar(@{$map->[$y]}); $x++) {
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

sub read_stack {
  my $line = shift;

  foreach my $i (0..($nb_stacks-1)) {
    my $idx = $i * 4 + 1;
    if ($idx <= length($line)) {
      my $letter = substr($line, $i * 4 + 1, 1);
      debug(3, "Stack $i: $letter\n");
      push(@{$stacks[$i]}, $letter) if ($letter =~ /[A-Z]/);
    }
  }
}

sub revert_stacks {
  my @tmp;
  foreach my $i (0..($nb_stacks-1)) {
    @{$tmp[$i]} = reverse @{$stacks[$i]};
  }

  @stacks = @tmp;
} 

sub move_stack {
  my ($nb, $from, $to) = @_;

  for (my $z = 0; $z < $nb; $z++) {
    my $l = pop(@{$stacks[$from-1]});
    push(@{$stacks[$to-1]}, $l);
  }
}

sub get_result {
  my $res = "";
  foreach my $stack (@stacks) {
    $res .= pop(@{$stack});
  }
  return $res;
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

# 1st read : identify number of stacks of crates
open(FILE, $file) or die("Cannot open file: $file\n");
while (<FILE>) {
  debug(3, "Read line: $_");
  chomp;
  if ($_ =~ /^ 1   2.*(\d)/) {
    $nb_stacks = $1;
    debug("Found that we have $nb_stacks stacks of crates\n");
    last;
  }
}
close(FILE);

# Create stacks
foreach my $i (0..($nb_stacks-1)) {
  @{$stacks[$i]} = ();
}

open(FILE, $file) or die("Cannot open file: $file\n");

my $result = 0;

while (<FILE>) {
  debug(3, "Read line: $_");
  chomp;

  if ($_ =~ /\[/) {
    read_stack($_);
  } elsif($_ =~ /^ 1/) {
    # Print stacks
    debug("Stacks before reverse:\n");
    debug(Dumper @stacks);
    # Revert each stack as the 1st items entered are actually the last in the stack
    revert_stacks();
    debug("Stacks after reverse:\n");
    debug(Dumper @stacks);
  } elsif ($_ =~ /move (\d+) from (\d+) to (\d+)/) {
    # Apply all movements
    move_stack($1, $2, $3);
  }
}
debug("Stacks after all movements:\n");
debug(Dumper @stacks);

close(FILE);

$result = get_result();

debug("\n===================================================================\n");
printf("Result: %s\n", $result);
