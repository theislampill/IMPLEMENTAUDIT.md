# SSD-L2 — Systems Security Engineering

[Family guide](README.md) · [Scientific sources and qualification limits](SOURCES.md#ssd-l2) · [Earlier documentary account](../SSD-L2.md)

This account explains the existing accepted scientific subject `c94ef360fb6c3115df8ef58256694433149f1744775d430406f1fedddebd7632` at its recorded scope. It preserves the study's conditions, adverse findings and unresolved questions; it is a documentary account of that science.

[Current property reader](SSD-L2-PROPERTIES.md) · [Structured scientific records](SSD-L2-PROPERTIES.json).

## 1. The scientific unit and its genealogy

Security Engineering asks which consequence must be protected, from which
adversarial or failure conditions, by which real enforcing mechanism, and with
what evidence and residual exposure. A control name, credential, checklist or
assurance label is insufficient without its protected object and threat model.
The accepted current population has 60 properties, 133 source records, 19 topic
groups, 14 genealogy relations, 20 criticism chains, 12 current tensions
reconciled with 22 native tensions, five configurations and 14 directed
relations. Four novelty candidates admit no new property identity.
[Accepted report; qualification; complete appendices.]

The typed history distinguishes Ware's whole-system context, Anderson's
reference-validation argument, Saltzer and Schroeder's design principles and
different formal policy traditions. Bell–LaPadula confidentiality does not
establish Biba integrity or Clark–Wilson transaction integrity. The confused
deputy belongs to Norman Hardy's specific account; it is not relabeled as a
Lampson result. Kerckhoffs-like convergence is not an authenticated direct
transmission claim. Later standards, engineering guidance and contemporary
supply-chain systems are related at their actual documentary and scientific
scopes rather than narrated as a single inevitable progression.
[Genealogy, all 14 edges; report's historical sections.]

## 2. Identity, authority and effect are distinct

Identity proofing, authentication, resource authorization and enforcement answer
different questions. A valid login supplies an identity input to policy; it
does not grant a particular export. Conversely, public access or a correctly
scoped bearer capability can be authorized without identifying a named person.
A security capability can convey bounded authority. The accurate distinction
is that technical ability or identity alone does not authorize arbitrary
effects, not a slogan that capabilities can never be permission.
[Composition R01; native P06, P16–P18.]

Delegation must bind the requested resource, operation and parameters to the
grant actually spent by the deputy. A filename supplied by a caller is not
enough when the deputy uses unrelated ambient write privilege. Revocation and
expiry also have consumer-specific semantics: disabling an account may leave
an offline signed token or derived session usable. A tolerated bounded expiry
window may suffice; every use need not introduce online revocation machinery.
The identity, effect-scope and currentness directions each leave issuer,
endpoint and wider policy premises open. [R01–R03.]

Separation of duties is similarly guarded. P07's r3 correction preserves the
possibility that one authorized actor with appropriate logging is adequate in
a bounded setting. Routine work, reversibility and low consequence do not by
themselves prove that this choice is cheaper or generally preferable. Adequacy,
obligations, threats and comparative total burden are separate axes. Creation,
transition, delay, privacy, maintenance and recovery costs belong to the same
relevant horizon; the adequate incumbent and no-change option remain live.
Unknown comparison remains unknown, without a reverse universal preference
for multiple actors. [Author narrative; P07 r3; qualification basis.]

## 3. Evidence does not expand its own scope

A formal proof can establish a logical invariant under its premises while
deployment correspondence remains unknown. Binary-level results may remove a
compiler assumption without removing hardware or boot assumptions. A timing
exclusion concerns the exact claim, not all possible security. One complete
finite check can be adequate for its small domain; a larger proof ceremony is
not intrinsically better. [P30–P31; R08.]

Three scanners sharing one oracle do not create three independent error paths.
An additional check is justified by a remaining consequential uncertainty, not
by a count. An old assurance result cannot prove its own currentness: the
actual change must be compared to a claim-relevant dependency set. Effective
runtime policy may differ from a correct configuration file on disk. A proved
irrelevant delta can preserve earlier evidence; unknown correspondence cannot
be silently promoted. [P25, P39, P48; R09, R13–R14.]

The r1 fidelity findings on P36 and P59 and the r2 adversarial finding on P07
remain attached to their earlier subjects. r2 narrowed provenance and diversity
overclaims; r3 corrected P07's comparative inference. P07 is the sole changed
property from r2, while other affected narrative and evidence objects were
updated. Exact unchanged earlier review scope is attributed rather than
re-described as an entirely fresh read of every source. Five nonblocking
advisories remain in the accepted qualification and are preserved in the
qualification appendix. [Author response; qualification; final review pair.]

## 4. Supply chains, updates and vulnerability decisions

An inventory can locate components and versions for affectedness triage. It
does not establish benign origin, reachability, exploitability or actual harm.
The accepted account preserves an inconsistency within S069's empirical
aggregate and withholds the unreconciled rate instead of inventing a corrected
effect estimate. CVSS intrinsic severity, threat/environment information and
EPSS's observed-CVE exploitation horizon are different from loss in a
particular installation. [P33, P35; R04; author narrative.]

Provenance ties an artifact digest to a stated builder/process claim under a
trusted policy. Best-effort completeness of recorded inputs cannot become
proof of every hidden production input or control-plane condition. A signature
can establish an authorized issuer for a particular digest and role while the
artifact remains malicious or defective. Authentic TUF update metadata does
not imply safe operation. Staged rollout requires representative observation,
workable fallback and an authorized safety state; it can miss a defect outside
the canary's coverage. [P36–P38; R05–R07.]

The reverse relations do not follow automatically. Successful deployment does
not prove issuer authority, a valid signature does not prove production
history, and general redundancy does not enforce update freshness. A directly
checked pinned component, one trusted-origin check or a small reversible
rollback can be a legitimate sufficient path for the narrower consumer.
These alternatives are evaluated at their actual consequence and obligation
scope. [R04–R07.]

## 5. Detection, containment, recovery and retirement

Telemetry supplies an observation within detector coverage. It does not
establish unobserved compromise or effective response; millions of attempts
are not millions of confirmed incidents. Integrity, context, privacy, triage
capacity and response authority condition the useful direction from
observation to action. One high-consequence event with a tested route can be
more useful than indiscriminate volume. [P40–P41; R10.]

Known derived credentials and control-plane grants must be revoked, expired or
isolated where they remain material to compromise. This can support restoration
without proving that unknown credentials, persistent hardware access or
compromised backups are absent. Uptime is not trustworthy restoration.
A clean rebuild still fails that concern if a known compromised recovery
administrator remains active. A small stateless rebuild with new grants can
close a declared known domain without an invented universal clean-room
programme. [P42–P44; R11–R12.]

Key and artifact roles matter during retirement. Executable authority,
verification material, decryption capability, evidence and recovery data have
different consumers. Indiscriminate deletion or rekeying can destroy valid
verification or recovery without addressing the real hostile authority.
Neither ordinary emergencies nor imagined unlimited future uses establish a
universal retention or rotation rule. [Accepted author narrative and property
reader, role-specific key/recovery properties.]

## 6. Configurations, costs and actual scientific limits

The five complete configurations cover ordinary bounded change, delegated
authority, supply-chain release, incident/recovery and proportionate assurance.
Their prerequisites, actual decision authority, evidence, alternatives,
omissions, cost, feedback and retirement appear in the exact composition
appendix. They are optional guarded configurations, not a serial lifecycle.
Activating more than one requires examining shared roots, repeated work,
conflicting failure policies and marginal value. [Composition profiles C1–C5.]

Tensions include logging versus privacy, least privilege versus emergency
response, fail-closed behavior versus availability, patching versus stability,
encryption versus recovery, centralized policy versus resilience, and
restoration versus forensic preservation. A standard or policy can establish a
requirement at its scope; it is not a field efficacy estimate. A producer's
preliminary incident account is not an independent investigation. Training
studies with different experimental and observational designs do not establish
one universal awareness effect. [Author narrative; criticism and tensions.]

The four rejected novelty proposals make useful distinctions without adding
primitives: mediated delegated effects are a configuration of existing
authority properties; trustworthy restoration is a guarded recovery chain;
authenticated provenance plus rollout remains separate obligations; and
"minimal current assurance" cannot claim a globally optimal portfolio from
local proportionality rules. An SBOM beside an unrelated training certificate
has no directed relation until a common receiving claim exists. [Composition
NC1–NC4 and arbitrary-co-use control.]

The executed original commission remains historically UNKNOWN. r3 did not
perform new external source access. Earlier adverse reviews, exposed cases and
unchanged-source reuse remain exact history. Acceptance covers this guarded
scientific interpretation and local explanatory correspondence, without
target deployment, measured effect, universal superiority or central/native
adoption. The 60-property current reader preserves complete current fields;
the separate public reader contains the 60 original historical public rows.


## Use in engineering

The receiving record names R002E / #198 as the existing Security/Privacy owner. Its existing evidence, identity, independent-challenge and acceptance routes remain the consumers. A later implementation question should compare the actual grant with the protected effect, configuration and recovery evidence. One complete bounded check can be sufficient without a new security subsystem.

The [existing responsibility outlines](../RLGWO_OUTLINES.md) identify preliminary comparison routes. A later engineering change needs a real consumer, the applicable existing owner and evidence for the exact implementation. These research findings do not appoint owners, create new issues or establish runtime effectiveness. Adequate existing controls, smaller methods and no change remain legitimate outcomes.

## Reading and evidence boundary

This public account normalizes already prepared derived research. Scientific examples retain their original classification as mathematical constructions, source-reported observations or empirical studies; none was rerun for this account. The [source notes](SOURCES.md) retain exact scientific identities, known source gaps and review limits. Current and historical records are separate populations, and a retention label is not the evaluated truth of every predicate.
