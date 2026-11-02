# PR255 ordinary broker acquisition receiving

This finite wave receives the existing PR251 owner's correction from
`d3cf2d465a474bd6ed2af7fb704678cdb6b8bc24` (tree
`35ca2bd6cb816ec42514855b388f4c76d366066b`) into the combined source based on
`34b5ea76b472d4605e8dda2ec22ce975284e3fc2`. Donor hosted run 40197954890 completed
successfully. Only the broker and its maintained regression test are received;
their combined preimages exactly equal the donor commit's parent preimages.
Other donor work and historical acceptance remain at their existing scopes.

The original broker hashed one file acquisition and displayed a second. An
actual combined-source interleaving recorded digest(A) while returning B after
the target changed. The retained donor control failed on that mismatch. The
correction captures one byte buffer, hashes it, and derives strict UTF-8 text
and universal-newline conversion from the same buffer. Existing target-root,
baseline, activation, journal and authority checks are unchanged.

PL4 source-fixture qualification: all eight unchanged acquisition controls pass
against the corrected combined source on Windows and within the full POSIX
bootstrap test. They cover stable and interleaved reads, interleaved literal
search, UTF-8/BOM/mixed newlines, search line numbering, case-sensitive no-match,
empty input and malformed UTF-8 refusal without a completed sink record. The
original combined-source failure and its raw recorded output remain retained.
The full bootstrap contract, capability-parity contract, read-only plans lane
and canonical validation-registry check also pass in WSL Ubuntu/Python 3.12.3.
The registry retains 91 tests and its one canonical CI route.

The broker SHA-256 is
`b5c3c9ffeda4c0903834eaaaff03db08bc7cd5001e45e3c74c3c669d92ba8168`;
the maintained test SHA-256 is
`7a4d6457766132e9f058f2274e2bc351b5dee8ed8729f3602665b7227339e1bd`.
Both are byte-identical to the qualified donor. The test keeps all original
assertions and scopes diagnostics to its temporary directory; its explicit
create-once capture option preserves the first outcome when requested.

These files are repository-only, not plugin or standalone runtime members.
Artifact source identity and hosted combined regression remain separate checks
for the published successor. Historical R0035 profiles, original 117-node
acceptance, prior failures and the approved revision-4 package contract are
unchanged. The ordinary probe's precondition and argument-sink stubs establish
bounded digest/view coherence, not an authenticated issuer, completed native
delivery, receiving acceptance, Stop/JOIN or whole-RLGWO completion. PR254 has
its own successor writer; this wave does not alter that branch or its evidence.
