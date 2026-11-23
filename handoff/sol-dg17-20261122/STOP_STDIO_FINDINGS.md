# DG17 Stop discovery stdin framing follow-up

**The benign control reproduced an unaccounted UTF-8 BOM.** On the tested Windows PowerShell 5.1 and .NET Framework, redirected stdin with stock console code page 65001 delivered `EF BB BF` plus the 150-byte initialize frame. The driver's BaseStream accounting still reported 150 bytes. With no explicit BaseStream write, the child received exactly the three BOM bytes. [Exact raw echo observations](STOP_STDIO_OBSERVATIONS.json).

## Historical operation

`DG17-STOP-PROFILE-DISCOVERY-001` remains **SPENT_NO_REPLAY**. Root reported 150 accounted stdin bytes, zero stdout bytes and a 178-byte stderr stream containing the JSON-RPC parse error at line 1, column 1. The historical driver captured the bytes it explicitly wrote. Its actual guest pipe bytes and live console input encoding remain unobserved. The benign control establishes a causal mechanism consistent with the failure. It does not identify the exact bytes in the spent guest. [Historical operator byte image](history/guest-r2.ps1.txt).

The archive is an exact inert copy of the historical `guest-r2.ps1`, 12,188 bytes, SHA-256 `2ed6fe2694fd08b344930fd8e5010d992804d83725b5bdbd68a54a0a3a5ce525`. Its presence grants no execution or retry. The packet carries no private native streams or host-specific worktree paths.

## What the echo child received

| Parent input encoding or case | Writer counted | Child received | Result |
|---|---:|---:|---|
| Private-console default and explicit stock 437 | 150 | 150 | Exact frame |
| Stock code page 65001 and explicit BOM-enabled UTF-8 | 150 | 153 | BOM followed by the exact frame |
| Stock 65001, no explicit write | 0 | 3 | BOM alone |
| Explicit BOM-free UTF-8 and guarded correction | 150 | 150 | Exact frame |
| Verified detached process with preamble-free cached input encoding | 150 | 150 | Exact frame without changing the encoding |
| Verified detached process with BOM-enabled cached encoding | — | — | Public encoding setter failed. The guard refused before starting a child. |

The fixture used the same `ProcessStartInfo` constructor, no-shell flag, redirected streams, BaseStream write and flush, and direct pipe closure as the historical driver. Its child read bounded raw bytes and returned hex before any decoding. A separate check compared those bytes to the exact frozen initialize line and ran strict UTF-8 string JSON decoding. BOM-prefixed inputs failed at position zero. Every preamble-free case carried the exact complete frame. The first `CreateNoWindow` wrapper still reported a console and was excluded from the detached controls. The successful detached controls explicitly detached an owned private-console fixture and verified `GetConsoleCP() == 0`. [Local-only probe source](STOP_STDIO_PROBE.ps1).

## Source and prospective correction

In .NET Framework, `Process.Start()` constructs the redirected stdin writer using `Console.InputEncoding` and enables its `AutoFlush`. The writer can emit the encoding preamble during that initialization, independently of later BaseStream writes. The exact installed PowerShell 5.1 runtime has no public `StandardInputEncoding` setter on `ProcessStartInfo`. [Framework Process](https://github.com/microsoft/referencesource/blob/ec9fa9ae770d522a5b5f0607898044b7478574a3/System/services/monitoring/system/diagnosticts/Process.cs), [Framework StreamWriter](https://github.com/microsoft/referencesource/blob/ec9fa9ae770d522a5b5f0607898044b7478574a3/mscorlib/system/io/streamwriter.cs).

Codex 0.153.4's stdio worker reads UTF-8 lines. It forwards each line directly to `serde_json::from_str::<JSONRPCMessage>`, and logs the deserialization error on refusal. The native protocol needs the plain newline-delimited JSON frame. No length header or startup byte prefix is used. [Pinned stdio read](https://github.com/openai/codex/blob/3d2ee51ca2d5db578f328aa75e20aa22c0197c9a/codex-rs/app-server-transport/src/transport/stdio.rs#L43), [pinned deserialization](https://github.com/openai/codex/blob/3d2ee51ca2d5db578f328aa75e20aa22c0197c9a/codex-rs/app-server-transport/src/transport/mod.rs#L208).

For a separately qualified future driver, inspect the actual `Console.InputEncoding.GetPreamble()` before arming `Process.Start()`. Keep it when empty. On an approved private console, set BOM-free UTF-8 when a preamble is present, then read back and require zero preamble bytes. Refuse before marking the child attempted if the public setter fails or the readback differs. This change belongs before process startup. Changing only the encoding used by `GetBytes()` leaves the constructor's preamble path in place. Keep the existing payload, bounded pipe exchange, custody and timing guards. Carry the actual local context and the zero-extra-byte control into any independent receiving. [Framework Console encoding setter](https://github.com/microsoft/referencesource/blob/ec9fa9ae770d522a5b5f0607898044b7478574a3/mscorlib/system/console.cs).

The correction was tested against benign children and remains prospective. This packet supplies no Stop acceptance, discovery completion, guest launch authorization, or request to launch another native operation.
