""" 
pwgen-lite
Minimalistic password generator in Python.

"""
import math
import argparse
import secrets
import string
import hmac
import os
from hashlib import sha256

__version__ = "1.0.0"

SCENARIOS = {
    "offline": 10.0,            # guesses/sec (rate-limited login-ish baseline)
    "offline-fast": 1e10,       # guesses/sec (fast GPU on weak hashes)
    "offline-very-fast": 1e11   # guesses/sec (very weak / highly optimized)
}

class HmacRng:

    """
    Educational HMAC-SHA256 based byte generator.
    Deterministic if the same seed is used.

    Not a full DRBG spec implementation; secrets-mode is recommended for real use. 
    """
    def __init__(self, key: bytes, context: bytes = b"pwgen-lite-hmac"):
        self.key = key
        self.context = context
        self.counter = 0
    
    def randbytes(self, n: int) -> bytes:
        out =bytearray()
        while len(out) < n:
            msg = self.counter.to_bytes(8, "big") + self.context
            block = hmac.new(self.key, msg, sha256).digest()
            out.extend(block)
            self.counter += 1
        return bytes(out[:n])

def estimate_entropy_bits(length: int, alphabet_size: int) -> float:
    """
    Entropy (in bits) for a uniformly random password
    bits = length * log2(alphabet_size)
    """
    if length <= 0 or alphabet_size <= 1:
        return 0.0
    return length * math.log2(alphabet_size)

def estimate_search_space(length: int, alphabet_size: int) -> int:
    """
    Total number of possible passwords for given length and alphabet size
    search_space = alphabet_size ** length
    """
    if length <= 0 or alphabet_size <= 1:
        return 0
    return alphabet_size ** length

def estimate_average_crack_time_seconds(search_space: int, guesses_per_second: float) -> float:
    """
    Expcted brute force time assuming attacker tries uniformly at random:
    average tries ~ 0.5 * search space
    time = tries / rate
    """
    if search_space <= 0 or guesses_per_second <= 0:
        return float("inf")
    return 0.5 * search_space / guesses_per_second

def format_duration(seconds: float) -> str:
    """
    Convert seconds into a human-friendly string.
    Keeps it simple: seconds, minutes, hours, days, years.
    """
    if seconds == float("inf"):
        return "infinite"
    if seconds < 1:
        return "< 1 second"

    units = [
        ("year", 365.25 * 24 * 3600),
        ("day", 24 * 3600),
        ("hour", 3600),
        ("minute", 60),
        ("second", 1),
    ]

    for name, size in units:
        if seconds >= size:
            value = seconds / size
            if value < 2:
                return f"{value:.2f} {name}"
            return f"{value:.2f} {name}s"

    return f"{seconds:.2f} seconds"



def bytes_to_password_hmac(length: int, alphabet: str, rng: HmacRng) -> str:
    """
    Convert HMAC-RNG bytes into password characters using rejcetion sampling to avoid modulo bias.
    """
    alph_len = len(alphabet)
    if alph_len < 2:
        raise ValueError("Alphabet too small.")
    
    #Largest multiple of alph_len less than 256 to avoid bias
    limit = (256 // alph_len) * alph_len

    chars = []
    while len(chars) < length:
        b = rng.randbytes(1)[0]
        if b >= limit:
            continue
        chars.append(alphabet[b % alph_len])
    
    return "".join(chars)

def build_alphabet(use_symbols: bool, exclude_ambiguous: bool) -> str:
    alphabet = BASE_ALPHABET + (SYMBOLS if use_symbols else "")
    if exclude_ambiguous:
        for ch in "O0Il1":
            alphabet = alphabet.replace(ch, "")
    return alphabet

# Base character sets
BASE_ALPHABET = string.ascii_letters + string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{}|;:,.<>?/~`"

def generate_password(length: int, use_symbols: bool, exclude_ambiguous: bool) -> str:
    """
    Generate a password of given length using secure randomness
    """

    alphabet = build_alphabet(use_symbols, exclude_ambiguous)
    return "".join(secrets.choice(alphabet) for _ in range(length))

def generate_password_hmac(length: int, use_symbols: bool, exclude_ambiguous: bool, seed: bytes) -> str:
    """
    Generate a password using the HMAC-based RNG for educational purposes.
    """
    alphabet = build_alphabet(use_symbols, exclude_ambiguous)
    rng = HmacRng(seed)
    return bytes_to_password_hmac(length, alphabet, rng)

def parse_arguments():
    """
    Parse command-line arguments.
    """

    parser = argparse.ArgumentParser(description="Generate a secure random password.")

    parser.add_argument("length", type=int, help="Length of the password (positive integer)")
    parser.add_argument("--count", type=int, default=1, help="Number of passwords to generate (default: 1)")
    parser.add_argument("--symbols", action="store_true", help="Include symbols in the password")
    parser.add_argument("--exclude-ambiguous", action="store_true", help="Exclude ambiguous characters (O,0,l,I,1)")
    parser.add_argument("--mode", choices=["secrets", "hmac"], default="secrets", help="RNG mode: secrets (recommended) or hmac (educational)")
    parser.add_argument("--seed-hex", default=None, help="(hmac mode) 32-byte seed as 64 hex characters. If omitted, a random seed is used.")
    parser.add_argument("--scenario", choices=list(SCENARIOS.keys()), default="offline-fast", help="Brute-force scenario for time estimate (default: offline-fast)")
    parser.add_argument("--rate", type=float, default=None, help="Override guesses/sec used for estimate (e.g. 1e10)")
    parser.add_argument("--no-strength", action="store_true", help="Do not print entropy / brute-force estimate")
    parser.add_argument("--version", action="version", version=f"pwgen-lite {__version__}", help="Show Programs current version")   

    return parser.parse_args()                    

def main():
    args = parse_arguments()

    # --- validate inputs ---
    if args.count <= 0: 
        print("Error: Count must be greater than 0.")
        raise SystemExit(2)
        return
    
    if args.length <= 0:
        print("Error: Length must be a positive integer.")
        raise SystemExit(2)
        return
    alphabet = build_alphabet(args.symbols, args.exclude_ambiguous)

    # --- build alphabet ONCE (used for entropy + generation) ---
    alphabet = build_alphabet(args.symbols, args.exclude_ambiguous)

    # --- print strength estimate if not disabled ---
    if not args.no_strength:
        A = len(alphabet)
        L = args.length
        bits = estimate_entropy_bits(L, A)
        space = estimate_search_space(L, A)

        rate = args.rate if args.rate is not None else SCENARIOS[args.scenario]
        avg_seconds =  estimate_average_crack_time_seconds(space, rate)

        print(f"alphabet: {A} chars")
        print(f"entropy: {bits:.2f} bits")
        print(f"{args.scenario} ({rate:g} guesses/s): ~{format_duration(avg_seconds)} (avg)")
        print()  # blank line before passwords

    # --- Generate seed + RNG once for hmac mode (so --count works properly) ---
    rng = None
    if args.mode == "hmac":
        if args.seed_hex is not None:
            try:
                seed = bytes.fromhex(args.seed_hex)
            except ValueError:
                print("Error: Invalid seed hex string. Must be 64 hex characters for 32 bytes.")
                raise SystemExit(2)
            
            if len(seed) != 32:
                print("Error: Seed must be exactly 32 bytes (64 hex characters).")
                raise SystemExit(2)
                
        else:
            seed = os.urandom(32)

        rng = HmacRng(seed)
    
    # --- Generate and print passwords ---
    for _ in range(args.count):
        if args.mode == "secrets":
            pw = "".join(secrets.choice(alphabet) for _ in range(args.length))
        else:
            # draws from the same RNG stream each time -> different pw per line,
            pw = bytes_to_password_hmac(args.length, alphabet, rng)
        
        print(pw)

               
if __name__ == "__main__":
    main()