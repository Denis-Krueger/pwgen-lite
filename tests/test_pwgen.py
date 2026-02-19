import string

import pwgen

def test_length_without_symbols():
   pw = pwgen.generate_password(32, use_symbols=False)
   assert len(pw) == 32

def test_length_with_symbols():
   pw = pwgen.generate_password(48, use_symbols=True)
   assert len(pw) == 48

def test_characters_without_symbols():
   allowed = set(string.ascii_letters + string.digits)
   pw = pwgen.generate_password(128, use_symbols=False)
   assert set(pw).issubset(allowed)

def test_charset_with_symbols():
    allowed = set(string.ascii_letters + string.digits + pwgen.SYMBOLS)
    pw = pwgen.generate_password(128, use_symbols=True)
    assert set(pw).issubset(allowed)
