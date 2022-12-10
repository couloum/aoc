#!/usr/bin/perl -w

#use Data::Dumper;
#use List::Util qw/min max/;

use strict;

my $DEBUG = 0;
my $sizes = {};


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

sub add_file {
  my $size = shift;
  my @local_path = @_;

  my $full_path = "";
  foreach my $dir (@local_path) {
    $full_path .= $dir . "/";
    $sizes->{$full_path} = 0 unless($sizes->{$full_path});
    $sizes->{$full_path} += $size;
    debug(3, "  Size of $full_path: ". $sizes->{$full_path} . "\n");
  }

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

my @path = ();

while (my $line = <FILE>) {
  debug(3, "Read line: $line");
  chomp $line;
  if ($line =~ /^\$ cd \.\./) {
    pop(@path);
    debug(3, "Go in previous directory. Current path: ".join('/', @path)."\n");
  } elsif ($line =~ /^\$ cd \//) {
    debug(3, "Nothing\n");
    push(@path, "");
  } elsif ($line =~ /^\$ cd (.*)/) {
    push(@path, $1);
    debug(3, "Go in directory $1. Current path: ".join('/', @path)."\n");
  } elsif ($line =~ /^\$/) {
    debug(3, "Nothing\n");
  } elsif ($line =~ /dir (.*)/) {
    debug(3, "Nothing\n");
  } elsif ($line =~ /^(\d+) /) {
    add_file($1, @path);
  }
}

close(FILE);

# Total used size
my $total_used = $sizes->{"/"};
my $total_free = 70000000 - $total_used;
my $required = 30000000 - $total_free;
debug("Total used size: $total_used. Total free size: $total_free. Needed space: $required\n");

# Get smallest directory with size at leat $required
foreach my $dir (sort {$sizes->{$a} <=> $sizes->{$b}} keys %$sizes) {
  my $s = $sizes->{$dir};
  debug("Size of $dir: $s");
  if ($s < $required) {
    debug(" - IGNORE\n");
    next;
  }
  debug(" - OK\n");
  $result = $s;
  last;
}

debug("\n===================================================================\n");
printf("Result: %d\n", $result);
