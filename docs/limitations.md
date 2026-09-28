# Limitations

This project is an HTML/JSON-LD quality-control utility, not a browser, crawler, or Google Search simulator.

## Supported input

The current version works best with server-rendered HTML containing FAQ content in conventional heading/paragraph, definition-list, or summary structures.

## Not fully detected

The parser may not identify FAQ content when it is:

- generated only after JavaScript execution
- rendered inside a shadow DOM
- represented by an unusual custom component
- loaded from an API after the initial HTML response
- visually presented without a recognizable question/answer structure

## Structured-data scope

The checker validates the FAQPage structures it understands. It does not attempt to implement the complete Schema.org vocabulary.

It also does not replace:

- Schema.org Validator
- Google's Rich Results Test
- Google Search Console
- browser-based inspection

## Search appearance

The project does not predict whether Google will display a rich result or another search feature.

Its findings concern the supplied implementation and visible content only.

## Matching

Exact normalized text matching is intentionally conservative. Two statements that are semantically equivalent but worded differently can be reported as mismatched.

## Future work

Potential future improvements should be evaluated against real user needs and the project's differentiation requirement before implementation.
