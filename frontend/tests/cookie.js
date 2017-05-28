import test from 'tape';
import {read_cookie, write_cookie} from '../js/cookie.js';

test('non-existing cookies are undefined', function(t) {
    global.document = {};
    global.document.cookie = '';
    t.deepEqual(read_cookie('foo'), undefined);
    t.end();
});

test('cookies can be written and read', function(t) {
    global.document = {};
    global.document.cookie = '';
    write_cookie('name', 'value');
    t.equals(read_cookie('name'), 'value');
    t.end();
});

test('cookie expiration date can be set', function(t) {
    global.document = {};
    global.document.cookie = '';
    write_cookie('name', 'value', 4);
    t.equals(global.document.cookie.substring(46, 50), 'GMT;');
    t.end();
});

test('when reading cookies, initial spaces are skipped', function(t) {
    global.document = {};
    global.document.cookie = ' name=value;';
    t.equals(read_cookie('name'), 'value');
    t.end();
});
