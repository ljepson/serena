#!/usr/bin/env perl
use strict;
use warnings;
use FindBin qw($Bin);
use lib "$Bin/lib";

use Models qw(User Item Order);
use Utils qw(format_currency calculate_discount);

sub main {
    my $user = User->new(
        id    => 1,
        name  => "John Doe",
        email => "john@example.com"
    );

    print "User info: " . $user->full_info() . "\n";

    my $item = Item->new(
        id    => 101,
        name  => "Widget",
        price => 29.99
    );

    print "Item: " . $item->description() . "\n";

    my $order = Order->new();
    $order->add_item($item, 2);

    my $total = $order->get_total();
    print "Order total: " . format_currency($total) . "\n";

    my $discounted_total = calculate_discount($total, 10);
    print "After 10% discount: " . format_currency($discounted_total) . "\n";

    # Demonstrate some complex references
    my $order_data = $order->to_hash();
    print "Order has " . scalar(@{$order_data->{items}}) . " item types\n";
}

sub helper_function {
    my ($number) = @_;
    $number //= 42;
    
    my $demo = DemoClass->new($number);
    return $demo->get_value() + 10;
}

package DemoClass;

sub new {
    my ($class, $value) = @_;
    return bless { value => $value }, $class;
}

sub get_value {
    my $self = shift;
    return $self->{value};
}

sub set_value {
    my ($self, $value) = @_;
    $self->{value} = $value;
}

package main;

main() if __FILE__ eq $0;