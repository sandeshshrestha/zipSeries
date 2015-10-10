#!/usr/bin/env perl

use 5;
use strict;
use warnings;

use Cwd 'abs_path';
use File::Basename;

my $root_dir = dirname(abs_path($0));
my $zipSeries = "python $root_dir/zipSeries.py";

my %args;

my $opt;
foreach (@ARGV) {
	if (m/--help/) {
		print "usage zipSeriesPrompt [--version] | [--help] | [zipSeries OPTION]...\n";
		print "\n";
		print "This is an interactive prompt for zipSeries. You can specify all of the same arguments as you can for zipSeries\n";
		print "\n";
		print "  --version      output version information and exit\n";
		print "    --help       show this help message and exit\n";
		exit 0;
	}
	elsif (m/--version/) {
		print "zipSeriesPrompt version=1.0.0\n";
		exit 0;
	}
	elsif (m/^-/) {
		$opt = $_;
	}
	else {
		$args{$opt} = $_; 
	}
}

open my $fh_help, "$zipSeries --help |" or die $!;
while (<$fh_help>) {
	if (m/^\s*options:\s*$/) {
		last;
	}
	if (m/^\s{0,10}-/) {
	
		my ($opt, $desc) = $_ =~ /(--.*?)\s+(.*?)$/;	

		if (not exists $args{$opt}) {
			print "Please enter $opt -- $desc: ";

			my $value = <STDIN>;
			$value =~ s/\s+$//;

			if ($value ne "") {
				$value =~ s/\s+$//;
				$args{$opt} = $value;
			}
		}
	}
}

close $fh_help;

my $cmd = "$zipSeries";
$cmd .= " \\\n    $_ \"$args{$_}\"" foreach (keys % args);

print "The followingg command will be run:\n";
print "$cmd ";
print "\n";

system("$cmd");
