#!/usr/bin/env perl

use strict;
use warnings;
use Test::More tests => 15;
use FindBin qw($Bin);
use lib "$Bin/../lib";

use_ok('Models', qw(User Item Order));

# Test User class
subtest 'User class tests' => sub {
    plan tests => 6;
    
    my $user = User->new(
        id    => 1,
        name  => 'John Doe',
        email => 'john@example.com'
    );
    
    isa_ok($user, 'User');
    is($user->get_id(), 1, 'User ID is correct');
    is($user->get_name(), 'John Doe', 'User name is correct');
    is($user->get_email(), 'john@example.com', 'User email is correct');
    
    like($user->full_info(), qr/John Doe.*ID: 1.*john\@example\.com/, 'Full info includes all details');
    
    my $hash = $user->to_hash();
    is_deeply($hash, {
        id    => 1,
        name  => 'John Doe',
        email => 'john@example.com'
    }, 'to_hash returns correct structure');
};

# Test Item class
subtest 'Item class tests' => sub {
    plan tests => 5;
    
    my $item = Item->new(
        id    => 101,
        name  => 'Widget',
        price => 29.99
    );
    
    isa_ok($item, 'Item');
    is($item->get_id(), 101, 'Item ID is correct');
    is($item->get_name(), 'Widget', 'Item name is correct');
    is($item->get_price(), 29.99, 'Item price is correct');
    
    my $discounted = $item->discounted_price(10);
    is(sprintf('%.2f', $discounted), '26.99', '10% discount calculated correctly');
};

# Test Order class
subtest 'Order class tests' => sub {
    plan tests => 4;
    
    my $order = Order->new();
    isa_ok($order, 'Order');
    
    my $item1 = Item->new(id => 1, name => 'Item1', price => 10.00);
    my $item2 = Item->new(id => 2, name => 'Item2', price => 15.50);
    
    $order->add_item($item1, 2);
    $order->add_item($item2, 1);
    
    is($order->get_total(), 35.50, 'Order total calculated correctly');
    
    my $items = $order->get_items();
    is(scalar(@$items), 2, 'Order has correct number of item entries');
    
    my $order_hash = $order->to_hash();
    ok(exists $order_hash->{items} && exists $order_hash->{total}, 'Order hash has required keys');
};

# Test static methods
subtest 'Static methods tests' => sub {
    plan tests => 2;
    
    my $default_user = User->default_user();
    isa_ok($default_user, 'User');
    is($default_user->get_name(), 'Guest', 'Default user has correct name');
};