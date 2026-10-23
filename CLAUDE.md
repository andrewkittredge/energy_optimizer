# CLAUDE.md

## Conventions

Implement the minimum feature set that satisfies the request, following "you aren't gonna need it" (YAGNI) closely. Don't add CLI flags, options, fallbacks, abstractions, configurability, or "while I'm here" extras that the request doesn't call for; don't build for hypothetical future needs. If something seems like it will be needed later, say so in a sentence rather than building it. When an existing feature turns out to be unused, remove it rather than keeping it around.

Avoid closures: don't define a function inside another function to capture the outer function's variables. When a callable needs configuration (a model id, an API client, a threshold), make it a module-level function that takes that configuration as explicit parameters and bind the fixed arguments with `functools.partial`, or put the state on a small `@dataclass` with a `__call__` method. Module-level functions can be imported, tested and debugged on their own; a closure can only be reached through the factory that built it, and its captured state is invisible from outside.
