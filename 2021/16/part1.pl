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

  push(@packets, $version);

  if ($type == 4) {
    ($value, $remain) = get_value(substr($packet, 6));
    debug 2, "  -> Packet is literal value with value=$value\n";
  } else {
    my $ltype = substr($packet, 6, 1);

    if ($ltype == 0) {
      my $length = bits_to_dec(substr($packet, 7, 15));
      debug 2, "  -> Packet is operator, with length type $ltype and length $length\n";
      $remain = substr($packet, 22, $length);
      while ($remain =~ /1/) {
        my ($tver, $ttype, $tval, $trem, @tpac) = decode_packet($remain);
        $remain = $trem;
        debug 3, "Remaining after decode: $remain\n";
        push(@packets, @tpac);
      }

      $remain = substr($packet, 22 + $length);
    } else {
      my $nbsub = bits_to_dec(substr($packet, 7, 11));
      debug 2, "  -> Packet is operator, with length type $ltype and nb sub packets $nbsub\n";
      $remain = substr($packet, 18);
      for (my $i = 0; $i < $nbsub; $i++) {
        my ($tver, $ttype, $tval, $trem, @tpac) = decode_packet($remain);
        $remain = $trem;
        push(@packets, @tpac);
      }
    }
  }

  # Remove padding bits
  if ($remain =~ /^0+$/) {
    $remain = "";
  }

  return ($version, $type, $value, $remain, @packets);
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

sub get_sum_version {
  my ($packet) = @_;

  my $sum = 0;

  debug "Analyzing raw packet $packet\n";
  my $packet_bits = hex_to_bits($packet);
  debug "Found bits: $packet_bits\n";
  my ($version, $type, $value, $remain, @packets) = decode_packet($packet_bits);
  debug "Found a total of ", scalar(@packets), " sub packets\n";

  foreach my $tver (@packets) {
    $sum += $tver;
  }
  return $sum
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

$result = get_sum_version($packet);

debug("\n===================================================================\n");
printf("Result: %d\n", $result);
