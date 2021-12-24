#!/usr/bin/perl -w

#use Data::Dumper;
use List::Util qw/min max sum/;

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

sub bits_to_dec {
  my ($bits) = @_;
  
  my $dec = 0;;
  for (my $i = 0; $i < length($bits); $i++) {
    $dec <<= 1;
    $dec += substr($bits, $i, 1);
  }
  debug 3, "  [bits_to_dec] $bits -> $dec\n";
  return $dec;
}

sub get_value {
  my ($bits) = @_;

  my @b = split('', $bits);
  my $dec = 0;
  while (@b) {
    my $t = shift(@b);
    my $v = join('', splice(@b, 0, 4));
    debug 3, "  [get_value] $t $v\n";
    $dec <<= 4;
    $dec += bits_to_dec($v);
    if ($t == 0) {
      last;
    }
  }

  debug 3, "  [get_value] $bits -> $dec. Remain: ", @b, "\n";
  return ($dec, join('', @b));
}

sub decode_packet {
  my ($packet) = @_;

  my @packets = ();
  my $value;
  my $remain = "";

  debug 2, "Decoding raw packet $packet\n";
  # Get bits from string
  my $version = bits_to_dec(substr($packet, 0, 3));
  my $type = bits_to_dec(substr($packet, 3, 3));

  debug 2, "  -> version is $version, type is $type\n";


  if ($type == 4) {
    ($value, $remain) = get_value(substr($packet, 6));
    debug 2, "  -> Packet is literal value with value=$value\n";
  } else {
    my $ltype = substr($packet, 6, 1);

    my @values = ();

    if ($ltype == 0) {
      my $length = bits_to_dec(substr($packet, 7, 15));
      debug 2, "  -> Packet is operator, with length type $ltype and length $length\n";
      $remain = substr($packet, 22, $length);
      while ($remain =~ /1/) {
        my ($tver, $ttype, $tval, $trem) = decode_packet($remain);
        $remain = $trem;
        debug 3, "Remaining after decode: $remain\n";
        push(@values, $tval);
      }

      $remain = substr($packet, 22 + $length);
    } else {
      my $nbsub = bits_to_dec(substr($packet, 7, 11));
      debug 2, "  -> Packet is operator, with length type $ltype and nb sub packets $nbsub\n";
      $remain = substr($packet, 18);
      for (my $i = 0; $i < $nbsub; $i++) {
        my ($tver, $ttype, $tval, $trem) = decode_packet($remain);
        $remain = $trem;
        push(@values, $tval);
      }
    }

    debug 2, "  -> Containing values ", join(', ', @values), "\n";

    if ($type == 0) {
      debug 2, "Calculating sum of values\n";
      $value = sum(@values);
    } elsif ($type == 1) {
      debug 2, "Calculating product of values\n";
      $value = 1;
      foreach my $tval (@values) {
        $value *= $tval;
      }
    } elsif ($type == 2) {
      debug 2, "Calculating minimum value\n";
      $value = min(@values);
    } elsif ($type == 3) {
      debug 2, "Calculating maximum value\n";
      $value = max(@values);
    } elsif ($type == 5) {
      debug 2, "Calculating greater than value\n";
      $value = 0;
      $value = 1 if ($values[0] > $values[1]);
    } elsif ($type == 6) {
      debug 2, "Calculating lesser than value\n";
      $value = 0;
      $value = 1 if ($values[0] < $values[1]);
    } elsif ($type == 7) {
      debug 2, "Calculating equal value\n";
      $value = 0;
      $value = 1 if ($values[0] == $values[1]);
    }

    debug 2, "  -> Operator packet value is $value\n";
  }

  # Remove padding bits
  if ($remain =~ /^0+$/) {
    $remain = "";
  }

  return ($version, $type, $value, $remain);
}

sub hex_to_bits {
  my ($packet) = @_;

  my %map = (
    0 => '0000',
    1 => '0001',
    2 => '0010',
    3 => '0011',
    4 => '0100',
    5 => '0101',
    6 => '0110',
    7 => '0111',
    8 => '1000',
    9 => '1001',
    A => '1010',
    B => '1011',
    C => '1100',
    D => '1101',
    E => '1110',
    F => '1111',
  );
  my $bits = "";
  for (my $i = 0; $i < length($packet); $i++) {
    $bits .= $map{substr($packet, $i, 1)};
  }

  return $bits;
}

sub get_result {
  my ($packet) = @_;

  debug "Analyzing raw packet $packet\n";
  my $packet_bits = hex_to_bits($packet);
  debug "Found bits: $packet_bits\n";
  my ($version, $type, $value, $remain) = decode_packet($packet_bits);
  debug "Found a final value of $value\n";

  return $value
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

my $packet = <FILE>;
chomp $packet;

close(FILE);

$result = get_result($packet);

debug("\n===================================================================\n");
printf("Result: %d\n", $result);
