#!/usr/bin/perl -W

use strict;

while (my $line = <STDIN>)
{
  $line =~ /\\indexentry{(.*)}{([^{}]+)}\s*$/;
  my $a = $1;  # name
  my $p = $2;  # pageref
  my $s = $a;  # name
  $s =~ s/\\IeC //g;
  $s =~ s/\\[^[:alpha:]]//g;
  $s =~ s/ }//g;
  $s =~ s/~/ /g;
  $s =~ s/[^[:alpha:], ~-]//g;
  print "\\indexentry{$s\@$a}{$p}\n";
}
