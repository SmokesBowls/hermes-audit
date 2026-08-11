# ENGAV3D-0001 Amendment 3
# Stage 6A JSON Parser Structural-Test Correction

## Purpose

This amendment corrects one defective Stage 6A structural test assertion.

It does not change the Stage 6 mailbox contract.
It does not authorize a production implementation change.
It does not loosen malformed-response rejection.
It does not authorize Hermes, provider, HTTP, or socket execution.

## Defective assertion

The frozen Stage 6A bridge test required the literal source fragment:

JSON.parse

This is not the required Godot error-aware parsing form.

The implemented bridge uses an instantiated JSON parser:

var parser := JSON.new()
var parse_result := parser.parse(...)

and inspects parser error state.

That is the intended error-aware parser lifecycle.

The static Godot convenience API is JSON.parse_string(...), which is a
different interface and is not required by Stage 6.

## Corrected structural requirement

The Stage 6A bridge source must demonstrate:

- construction of a JSON parser instance with JSON.new();
- invocation of the parser instance's parse(...) method;
- inspection of parser error information;
- dictionary/root-type validation;
- exact response-key validation;
- RESPONSE_SCHEMA validation.

The structural test therefore must not require a literal static:

JSON.parse(...)

Instead it must require JSON.new() and an instance .parse(...) call.

## Authority transition

Superseded bridge-test SHA-256:

70a1c5b461b019c8f572300c89d51f364c7dcbccc5d2d639d70275ac868bcc1b

The filesystem test authority remains unchanged:

36c1b3af84c6b40d87e02cf3f399c494f8068ffdc8b9a3d5d6aaab2dc6757b67

A new bridge-test SHA-256 becomes authoritative only after this amendment
is sealed and the single defective assertion is corrected.

No other Stage 6A test behavior may change.
