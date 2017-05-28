import test from 'tape';
import {intersection} from '../js/utils.js';

test('intersection of two empty arrays is an empty array', function(t) {
    t.deepEqual([], intersection([], []));
    t.end();
});

test('intersection with first array empty is an empty array', function(t) {
    t.deepEqual([], intersection([], [1, 2]));
    t.end();
});

test('intersection with second array empty is an empty array', function(t) {
    t.deepEqual([], intersection([1, 2], []));
    t.end();
});

test('intersection of equal arrays equals both arrays', function(t) {
    t.deepEqual([1, 2], intersection([1, 2], [1, 2]));
    t.end();
});

test('intersection of differently ordered equal arrays equals first array', function(t) {
    t.deepEqual([1, 2], intersection([1, 2], [2, 1]));
    t.end();
});

test('intersection of different arrays is empty', function(t) {
    t.deepEqual([], intersection([1, 2], [3, 4]));
    t.end();
});

test('intersection of overlapping arrays is the overlap', function(t) {
    t.deepEqual([2], intersection([1, 2], [2, 3]));
    t.end();
});

