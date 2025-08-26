use strict;
use warnings;
use ExtUtils::MakeMaker;

WriteMakefile(
    NAME               => 'TestRepo',
    AUTHOR             => 'Test Author <test@example.com>',
    VERSION_FROM       => 'lib/Models.pm',
    ABSTRACT           => 'Test repository for Perl Language Server',
    LICENSE            => 'perl',
    MIN_PERL_VERSION   => '5.016',
    CONFIGURE_REQUIRES => {
        'ExtUtils::MakeMaker' => '0',
    },
    BUILD_REQUIRES => {
        'Test::More' => '0',
    },
    PREREQ_PM => {
        'strict'   => '0',
        'warnings' => '0',
        'Exporter' => '0',
        'FindBin'  => '0',
        'POSIX'    => '0',
    },
    META_MERGE => {
        'meta-spec' => { version => 2 },
        resources   => {
            repository => {
                type => 'git',
                url  => 'https://github.com/example/test-repo.git',
                web  => 'https://github.com/example/test-repo',
            },
        },
    },
    dist  => { COMPRESS => 'gzip -9f', SUFFIX => 'gz', },
    clean => { FILES => 'TestRepo-*' },
);