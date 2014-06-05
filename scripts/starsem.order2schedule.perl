#!/usr/bin/perl -W
# Variant of order2schedule for STARSEM, where parallel Sessions are not synchronized

use strict;

my (@S, @P, @D);
my $conf_part = $ARGV[0];	# main / wsX / demo 
$conf_part = "main" unless $conf_part;

# PART I: Parse the order file (as provided by the program chair in the 
# aclpub bundle. 
# ATTENTION: This script is picky about proper use of '+' and '=' !!!
# You may have to fix the order file to get correct results.

my $auto = "auto/$conf_part";
mkdir $auto;

my ($day,$session,@papers, @times);
my ($session_start, $session_end, $session_slot, $session_title, $session_tag);
while (my $line = <STDIN>)
  {
    next if $line =~ /^\s*$/;
    while ($line and $line =~ /^([0-9]+)\s+([0-9:-]+)?/)
    {
      push @papers, $1;
      push @times, $2 if $2;
      $line = <STDIN>;
    }
    last unless $line;
    print $line;
    if (scalar(@papers))
    {
      $session_tag =~ tr/0123456789/ABCDEFGHI/;
      &print_papers;
      @papers = ();
      @times  = ();
    }
    if ($line =~ /^\* ([a-zA-Z]+)/)
    {
      $day = $1;
    }
    elsif ($line =~ /^\+ ORAL\s+([^ ]*)\s+([0-9:]+)\s*-+\s*([0-9:]+)\s+([0-9]+)\s+(.*)/)
    {
      $session_tag   = $1;
      $session_start = $2;
      $session_end   = $3;
      $session_slot  = $4;
      $session_title = $5;
    }
    elsif ($line =~ /^\+ POSTER\s+(.*?)\s+([0-9:]+)\s*-+\s*([0-9:]+)\s+(.*)/)
    {
      $session_tag   = $1;
      $session_start = $2;
      $session_end   = $3;
      $session_title = $4;
    }
  }
if (scalar(@papers))
{
  &print_papers;
  @papers = ();
  @times  = ();
}

sub print_papers
{
  print "$session_tag\n";
  my $bname = "$auto/".lc($day)."-$conf_part-$session_tag";
  print "$bname\n";
  open TEX, ">$bname.tex" or die "$!\n";
  open ABS, ">$bname-abstracts.tex" or die "$!\n";
  $session_start =~ m/([0-9]+):([0-9]+)/;
  my ($hhe,$mme) = ($1,$2);
  if (scalar(@times))
  {
    print TEX "\\begin{tabularx}{\\linewidth}{\@{}rX\@{}}\n";
    for (my $i = 0; $i < scalar(@papers); ++$i)
    {
      $times[$i] =~ /([0-9]+):([0-9]+)(?:\s*-+\s*([0-9]+):([0-9]+))?/;
      my ($hh1,$mm1,$hh2,$mm2) = ($1,$2,$3,$4);
      if (defined($hh2))
      {
	($hhe,$mme) = ($hh2,$mm2);
      }
      else
      {
	$mme += $session_slot;
	if($mme >= 60) { $hhe++; $mme -= 60; }
      }
      my $t = sprintf("%d:%02d--%d:%02d", $hh1, $mm1, $hhe, $mme);
      print ABS sprintf("\\paperabstract{$day}{$t}{%s}{\\%s}{%s-%03d}\n", 
			$session_title, $session_tag."loc", $conf_part, $papers[$i]);
      print TEX sprintf("$hh1:$mm1 & \\paperentry{$conf_part-%03d}\\\\\n", $papers[$i]);
    }
    print TEX "\\end{tabularx}\n";
  }
  else
  {
    for (my $i = 0; $i < scalar(@papers); ++$i)
    {
      my $t = "$session_start--$session_end";
      print ABS sprintf("\\paperabstract{$day}{$t}{%s}{\\%s}{%s-%03d}\n", 
			$session_title, $session_tag."loc", $conf_part, $papers[$i]);
      print TEX sprintf("\\paperentry{$conf_part-%03d}\\\\\n", $papers[$i]);
    }
  }
  close TEX;
  close ABS;
}
