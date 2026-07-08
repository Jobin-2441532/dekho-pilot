from pywebpush import generate_vapid_keypair
import json

vapid_keys = generate_vapid_keypair()
print("VAPID_PUBLIC_KEY=", vapid_keys['public_key'])
print("VAPID_PRIVATE_KEY=", vapid_keys['private_key'])
