#!/usr/bin/env perl

use strict;
use warnings;
use Test::More tests => 12;
use FindBin qw($Bin);
use lib "$Bin/../lib";

use_ok('Utils', qw(format_currency calculate_discount validate_email array_sum deep_clone));
use_ok('Utils::Math', qw(fibonacci factorial is_prime));
use_ok('Utils::String', qw(trim capitalize snake_to_camel));

# Test main Utils functions
subtest 'Currency formatting' => sub {
    plan tests => 3;
    
    is(Utils::format_currency(10), '$10.00', 'Integer formatting');
    is(Utils::format_currency(10.5), '$10.50', 'Decimal formatting');
    is(Utils::format_currency(10.567), '$10.57', 'Rounding formatting');
};

subtest 'Discount calculation' => sub {
    plan tests => 2;
    
    is(Utils::calculate_discount(100, 10), 90, '10% discount on 100');
    is(Utils::calculate_discount(50, 20), 40, '20% discount on 50');
};

subtest 'Email validation' => sub {
    plan tests => 4;
    
    ok(Utils::validate_email('test@example.com'), 'Valid email passes');
    ok(!Utils::validate_email('invalid.email'), 'Invalid email fails');
    ok(!Utils::validate_email(''), 'Empty email fails');
    ok(!Utils::validate_email(undef), 'Undefined email fails');
};

subtest 'Array utilities' => sub {
    plan tests => 2;
    
    is(Utils::array_sum(1, 2, 3, 4), 10, 'Array sum calculation');
    is(Utils::array_sum(), 0, 'Empty array sum is zero');
};

subtest 'Deep clone' => sub {
    plan tests => 2;
    
    my $original = {
        name => 'test',
        items => [1, 2, 3],
        nested => { value => 42 }
    };
    
    my $cloned = Utils::deep_clone($original);
    
    is_deeply($cloned, $original, 'Cloned structure matches original');
    
    # Modify clone to ensure it's independent
    $cloned->{name} = 'modified';
    isnt($original->{name}, $cloned->{name}, 'Clone is independent of original');
};

# Test Math utilities
subtest 'Math::fibonacci' => sub {
    plan tests => 4;
    
    is(Utils::Math::fibonacci(0), 0, 'fib(0) = 0');
    is(Utils::Math::fibonacci(1), 1, 'fib(1) = 1'); 
    is(Utils::Math::fibonacci(5), 5, 'fib(5) = 5');
    is(Utils::Math::fibonacci(10), 55, 'fib(10) = 55');
};

subtest 'Math::factorial' => sub {
    plan tests => 4;
    
    is(Utils::Math::factorial(0), 1, '0! = 1');
    is(Utils::Math::factorial(1), 1, '1! = 1');
    is(Utils::Math::factorial(5), 120, '5! = 120');
    is(Utils::Math::factorial(3), 6, '3! = 6');
};

subtest 'Math::is_prime' => sub {
    plan tests => 6;
    
    ok(!Utils::Math::is_prime(0), '0 is not prime');
    ok(!Utils::Math::is_prime(1), '1 is not prime');
    ok(Utils::Math::is_prime(2), '2 is prime');
    ok(Utils::Math::is_prime(17), '17 is prime');
    ok(!Utils::Math::is_prime(4), '4 is not prime');
    ok(!Utils::Math::is_prime(15), '15 is not prime');
};

# Test String utilities  
subtest 'String utilities' => sub {
    plan tests => 6;
    
    is(Utils::String::trim('  hello  '), 'hello', 'Trim whitespace');
    is(Utils::String::trim('hello'), 'hello', 'Trim no whitespace');
    
    is(Utils::String::capitalize('hello'), 'Hello', 'Capitalize first letter');
    is(Utils::String::capitalize('HELLO'), 'Hello', 'Capitalize with lowercase');
    
    is(Utils::String::snake_to_camel('snake_case'), 'snakeCase', 'Snake to camel case');
    is(Utils::String::snake_to_camel('another_test_case'), 'anotherTestCase', 'Multiple underscores');
};