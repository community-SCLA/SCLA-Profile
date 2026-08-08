# Design direction

The composition uses a clean editorial layout on deep navy. A persistent upper
label identifies the Career Transitions program. The one carrying object is the
**Pivot Story Bridge**: the same Backstory, Turning Point, and Forward Case tiles
remain on screen for the full lesson. Each beat re-sorts their emphasis along the
same blue route instead of discarding the frame. Gold identifies the tile doing
the current narrative work; the beat's supporting message changes inside one
fixed editorial field above it.

## Typography

Proxima Nova is preferred with the system sans-serif fallback. Headlines are
64–88px and supporting copy is 40–46px. Small labels remain at least 22px. Copy
is kept inside the 120px frame padding and above the 120px footer reserve.

## Motion

Each timed message enters with a 0.5-second rise-and-fade. Supporting elements
follow with a short stagger and settle within 1.2 seconds. The persistent Pivot
Story Bridge shifts focus by lifting and recoloring one of its three existing
tiles; it is never replaced. Each outgoing message fades in 0.3 seconds. All
movement is driven by one paused GSAP timeline and is deterministic at any seek
position.

## Beat treatments

- Opening: the listener's question appears between PAST and NOW.
- Research: a single evidence card centers “narrative coherence.”
- Structure: three numbered nodes form a connected route.
- Examples: paired “not this / say this” statements clarify reframing.
- Failure modes: warning cards are crossed out one at a time.
- Close: the route resolves into WRITE → COMPRESS → INSTALL.
