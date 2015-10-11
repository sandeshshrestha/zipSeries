#!/usr/bin/env perl

# zipSeriesPrompt
# 
# This is an interactive prompt for zipSeries. 
#   You can specify all of the same arguments as you can for zipSeries 
#

use strict;
use warnings;

use Cwd 'abs_path';
use File::Basename;

use constant VERSION => "1.0.0";

my $root_dir = dirname(abs_path($0));
my $zipSeries = "python $root_dir/zipSeries.py";

my %possible_zs_args = get_possible_zs_args();
my %zs_args = parse_argv();

# Prompt the remaining args that are not allready defined via CLI:
foreach (keys %possible_zs_args) {
	
	my $opt = $_;
	my $desc = $possible_zs_args{$opt};

	if (not exists $zs_args{$opt}) {
		print "Please enter $opt -- $desc: ";

		my $value = <STDIN>;
		$value =~ s/\s+$//;

		if ($value ne "") {
			$value =~ s/\s+$//;
			$zs_args{$opt} = $value;
		}
	}
}

# Run zipSeries command:
my $cmd = "$zipSeries";
$cmd .= " \\\n    $_ \"$zs_args{$_}\"" foreach (keys %zs_args);

print "The followingg command will be run:\n";
print "$cmd ";
print "\n";

system("$cmd");

# Subrutines:
sub get_possible_zs_args {

	my %args;
	open my $fh_help, "$zipSeries --help |" or die $!;
	while (<$fh_help>) {
		last if (m/^\s*options:\s*$/);
		
		if (m/^\s{0,10}-/) {
			# Capture: -c, (--command)      (description with spaces)
			my ($opt, $desc) = $_ =~ /(--.*?)\s+(.*?)$/;	
			$args{$opt} = $desc;
		}
	}
	close $fh_help;

	return %args;
}

sub print_help {
	print "usage zipSeriesPrompt [--version] | [--help] | [zipSeries OPTION]...\n";
	print "\n";
	print "This is an interactive prompt for zipSeries. You can specify all of the same arguments as you can for zipSeries\n";
	print "\n";
	print "zipSeries options:\n";
	print sprintf "  %-25s %-s\n", $_, $possible_zs_args{$_} foreach (keys %possible_zs_args);
	print "\n";
	print "options:\n";
	print "  --version                 output version information and exit\n";
	print "  --help                    show this help message and exit\n";
	exit 0;
}

sub print_version {
	print "zipSeriesPrompt version=" . VERSION . "\n";
	exit 0;
}

sub parse_argv {
	my %args;
	my $opt;
	foreach (@ARGV) {
		if (m/--help/) {
			print_help();
		}
		elsif (m/--version/) {
			print_version();
		}
		elsif (m/^-/) {
			$opt = $_;
		}
		else {
			$args{$opt} = $_; 
		}
	}
}
