# R003A prospective package capacity approval

On October 23, 2026, the human owner approved the concrete R003A capacity proposal:

> Approve 458,752-byte caps; retain 2,000-byte reserve

This prospective revision applies to both the canonical plugin and standalone
compatibility artifact roles. It preserves the 65,536-byte rounding increment,
runtime 0.4.0, release family v0.4.0.0, and every membership, integrity, source,
installation, rollback and runtime acceptance control.

The measured candidate was commit5358eb209d68ef4dcc457bace94b6f22d6105431,
tree7d7bbcfb3d0265ea629785e03b151f2156808fb5: plugin399739 bytes and
standalone395316 bytes. Both failed the prior393216-byte cap and2000-byte
reserve. The two repeated builds were byte-identical under the unchanged pinned
compressor. The minimum measured cap including reserve was401739 bytes;
458752 is the next existing rounding unit. Final candidate qualification remains
required after the approved revision and any source corrections.

Preserve budget revisions1 and2, their approval/evidence, and all original
capacity failures. This decision does not relabel those failures or grant merge,
issue closure, release, native host acceptance or protected campaign authority.
