# Design direction

The composition uses a clean editorial layout on deep navy. A persistent upper
label identifies the Career Transitions program and a slim progress route along
the bottom advances through thirteen beats. White cards represent evidence and
experience, blue lines represent connection, and gold is reserved for decisions,
numbers, and the final resolved bridge.

## Typography

Proxima Nova is preferred with the system sans-serif fallback. Headlines are
64–88px and supporting copy is 40–46px. Small labels remain at least 22px. Copy
is kept inside the 120px frame padding and above the 120px footer reserve.

## Motion

Each timed clip enters with a 0.5-second rise-and-fade. Supporting elements follow
with a short stagger and settle within 1.2 seconds. The route line draws from left
to right. Each outgoing clip fades in 0.3 seconds. All movement is driven by one
paused GSAP timeline and is deterministic at any seek position.

## Beat treatments

- Opening: the listener's question appears between PAST and NOW.
- Research: a single evidence card centers “narrative coherence.”
- Structure: three numbered nodes form a connected route.
- Examples: paired “not this / say this” statements clarify reframing.
- Failure modes: warning cards are crossed out one at a time.
- Close: the route resolves into WRITE → COMPRESS → INSTALL.
