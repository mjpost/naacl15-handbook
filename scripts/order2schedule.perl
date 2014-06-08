#!/usr/bin/perl -W

use strict;

my (@S, @P, @D);
my $conf_part = $ARGV[0];  # main / wsX / demo 
$conf_part = "main" unless $conf_part;

# PART I: Parse the order file (as provided by the program chair in the 
# aclpub bundle. 
# ATTENTION: This script is picky about proper use of '+' and '=' !!!
# You may have to fix the order file to get correct results.

my $auto = "auto/$conf_part";
mkdir $auto;

my $poster_file = "$auto/${conf_part}-poster-abstracts.tex";
print "writing to file $poster_file\n";
open (POSTERS, ">$poster_file") 
    or die "Could not open file '$poster_file': $!\n";

my $day;
my $session_no = 0;
my $session_name;
while (my $line = <STDIN>)
{
  next if $line =~ /^\s*$/;
  my $c = substr($line,0,1);
  if ($line =~ /^[+*]/ and $#P >= 0)
  {
    push @S, [@P];
    @P = ();
  }
  if ($c eq "*")    # DAY LINE
  {
    $session_no = 1;
    if ($#S >= 0)
    {
      die "Sessions without days!\n" unless $#D >= 0;
      push @{$D[$#D]}, [@S];
      @S = ();
    }
    $line =~ /\*\s*([a-zA-Z]+)/;
    my @d = ($1, ());
    push @D, [@d];
    $day = lc(shift @d);

    my $filename = "$auto/$day-$conf_part-abstracts.tex";
    print "writing to $filename\n";
    close SCHED;
    open (SCHED, ">$filename") 
        or die "Could not open file '$filename': $!\n";
  }
#  elsif ($line =~ /[+=]\s+Session\s+(.*?):/) # SESSION
  elsif ($line =~ /^= (.*?)$/) # SESSION
  {
    chomp($session_name = $1);
    $session_name =~ s/\r//g;
    print SCHED "\\clearpage\n";
    print SCHED "\\par\\centerline{\\bfseries\\large Session $session_name}\\vspace{1em}\\par\n";
  }
  elsif ($line =~ /([0-9]+)\s*([0-9: -]+)?\s*\#/)
  {
#    die "Papers without session ($line)!" unless $session_name;
    my $pid = $1;
    my $tim = $2 ? $2 : "";
    
    my $this_conf_part = $conf_part;
    if ($line !~ /^\d/) {
      my @tokens = split(' ', $line);
      ($this_conf_part,$pid) = split('-', $tokens[0]);
    }

    #print $#P, "@P\n:";
    my $d = $day;
    $d =~ s/(.)([a-z]+).*/uc($1).$2/e;
    my @tim = split(/\s*-+\s*/, $tim);
    if (scalar(@tim))
    {
      for (@tim)
      {  # add am / pm 
        s/\s+//g; 
        $_ = minus12($_);
        # /([0-9]+):/; 
        # $_ .= ($1 < 9 or $1 > 11) ? "pm" : "am"; 
      }
      my $d = $day;
      $d =~ s/(.)([a-z]+).*/uc($1).$2/e;
      my $t = "$tim[0]--$tim[1]";
      print SCHED sprintf("\\paperabstract{$d}{$t}{garbage}{garbage}{$this_conf_part-%03d}\n", $pid);
    }
    else
    {
      print POSTERS sprintf("\\posterabstract{$this_conf_part-%03d}\n", $pid);
    }
    #print "OOPS: $line";
  }
}

close(SCHED);
close(POSTERS);

exit;

# PART II: Write tex files to be \input{} in the latex document for the
# conference handbook.

for (@D)
{
  my @d = @{$_};
  my $day = lc(shift @d);

  # iterate through all the event blocks for this day
  for (my $i = 0; $i <= $#d; ++$i)
  {
    my $b = 1;
    @P = @{$d[$i]};     # a list of all things going on in parallel
    for (@P)
    {
      my $numslots = 0;
      @S = @{$_};

      # open the destination file for this event block / session
      my $bname = sprintf("$auto/$day-$conf_part-%d", $b++);
      open (TEX, ">$bname.tex") 
          or die "Could not open file '$bname.tex': $!\n";
      
      # determine the number of paper slots in the session
      for (@S)
      {
        my @p = @{$_};  # @p is an individual session
        shift @p;  # remove the session id 
        my $n = scalar(@p); # determine the number of paper slots in the session
        $numslots = $n if $numslots < $n;
      }
      
      # write slots in latex table format
      for (my $k = 1; $k <= $numslots; ++$k)
      {
        my @tim = ();  # start and end time
        my @r   = ();  # papers in this slot
        for (@S)
        {
          my @p = @{$_};
          next if scalar(@p) < $k;
          push @r, $p[$k][0];
          print "@r\n";
          #print "|$p[$k][1]|\n";
          next unless defined $p[$k][1];
          @tim = split(/\s*-+\s*/, $p[$k][1]) unless scalar(@tim);
        }
        #print "TIM @tim \n";
        if (scalar(@tim))
        {
          for (@tim)
          {    # add am / pm 
            s/\s+//g; 
            $_ = minus12($_);
            # /([0-9]+):/; 
            # $_ .= ($1 < 9 or $1 > 11) ? "pm" : "am"; 
          }
          print TEX "$tim[0] & -- & $tim[1]";
          print TEX sprintf(" & \\paperentry{$conf_part-%03d}", $_) for @r;
          print TEX "\\\\\\hline\n";
        }
        else
        {
          print TEX sprintf("\\posterentry{$conf_part-%03d}", $_) 
              for @r;
          print TEX "\\\\[1ex]\n";
        }
      }
      for (@S)
      {
        my @p = @{$_};
        my $session_title = shift @p;
        (my $s = $session_title) =~ s/-//;
        $s =~ tr/0-9/A-J/;
        my $absfile = "$bname-$s-abstracts.tex";
        open (ABS, ">$absfile")
            or die "Could not open file '$absfile': $!\n";
        
        for (@p)
        {
          my @x = @{$_};
          my @tim = split(/\s*-+\s*/, $x[1]);
          if (scalar(@tim))
          {
            for (@tim)
            {  # add am / pm 
              s/\s+//g; 
              $_ = minus12($_);
              # /([0-9]+):/; 
              # $_ .= ($1 < 9 or $1 > 11) ? "pm" : "am"; 
            }
            my $d = $day;
            $d =~ s/(.)([a-z]+).*/uc($1).$2/e;
            my $t = "$tim[0]--$tim[1]";
            print ABS sprintf("\\paperabstract{$d}{$t}{\\%s}{\\%s}{%s-%03d}\n",
                              $s."title", $s."loc", $conf_part, $x[0]);
          }
          else
          {
            #print ABS sprintf("\\posterabstract{$conf_part-%03d}\n", $x[0]);
            my $t = "6:30pm--8:30pm";
            my $d = "Monday";
            print ABS sprintf("\\paperabstract{$d}{$t}{%s}{\\%s}{%s-%03d}\\par\n",
                              "Poster Session", "PosterSessionLoc", 
                              $conf_part, $x[0]);
          }
        }
        close ABS;
      }
      close TEX;
    }
  }
}

sub minus12 {
  my ($hm) = @_;
  /(\d+):(\d+)/;
  my $hours = $1;
  my $minutes = $2;
  $hours -= 12 if ($hours >= 13);
  return "$hours:$minutes";
}
