Stage 6A structural-test correction evidence.

Superseded bridge-test authority:
70a1c5b461b019c8f572300c89d51f364c7dcbccc5d2d639d70275ac868bcc1b

Corrected bridge-test authority:
e15bdd515f7e362cbf7b9443528945e9c1f84d7cbb6ab445f5b3b7aaadf0ede0

The correction replaced the defective literal JSON.parse requirement with
the Godot error-aware JSON.new() plus instance .parse(...) requirement.

No production contract was loosened.
