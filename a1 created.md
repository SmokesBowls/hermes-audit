    Preservation-first A1 workspace created and verified:
    
    text
    /mnt/data-drive/engain_dragon_mettatext_A1/
    ├── README_A1_WORKSPACE.md
    ├── dragon/
    ├── engain/
    └── preservation/
    
    
    Copy baselines
    
    Dragon:
    
    text
    Branch: main
    HEAD: 29c84e25d5afd93d28f6f36c49d6278fba84a4cf
    Remote: git@github.com:SmokesBowls/godot_3d_avatar.git
    Tracked: 200
    Untracked: 3
    Ignored files preserved: 141
    
    
    EngAIn:
    
    text
    Branch: main
    HEAD: 7120f16e1997eb1684177e7a299454f1e024e77e
    Remote: git@github.com:SmokesBowls/EngAIn.git
    Tracked: 3,792
    Untracked: 1
    Ignored files preserved: 8,011
    
    
    Preserved untracked state
    
    Dragon:
    
    text
    snapshots/perception_cap_6812930ca01e3db4768d70482cdf9a09_3.json
    snapshots/perception_cap_6812930ca01e3db4768d70482cdf9a09_3.png
    snapshots/perception_cap_6812930ca01e3db4768d70482cdf9a09_3.png.import
    
    
    EngAIn:
    
    text
    docs/Canonical authority map — current local checkout august 30 2026.md
    
    
    Verification results
    
    All verification gates passed:
    
    - Tracked files in each copy match the corresponding original byte-for-byte by SHA-256.
    - Full copied trees match, including .git, untracked files, ignored files, modes, and symlinks.
    - Branches, HEADs, remotes, and porcelain status match.
    - A dry-run rsync -aniHAXS --numeric-ids --delete reported no differences for either copy.
    - All 11 EngAIn symlinks were preserved with identical targets and modes.
    - No omitted, changed, added, special, or failed-copy paths were found.
    - Pre-copy and post-copy full manifests of both originals matched exactly, including .git.
    - No commits or pushes occurred.
    - Neither project was launched.
    - A1 implementation was not started.
    
    The detailed report and machine-readable evidence are at:
    
    text
    /mnt/data-drive/engain_dragon_mettatext_A1/preservation/VERIFICATION_REPORT.md
    /mnt/data-drive/engain_dragon_mettatext_A1/preservation/verification_report.json
    
    
    The workspace is explicitly marked as non-canonical in:
    
    text
    /mnt/data-drive/engain_dragon_mettatext_A1/README_A1_WORKSPACE.md
    
    
    The IDE can now be opened at:
    
    text
    /mnt/data-drive/engain_dragon_mettatext_A1/
    
    
    No A1 code changes have been made.
Good. The preservation step is complete, and now the original Dragon and EngAIn repos are effectively our reference specimens. All A1 work can happen inside:

`/mnt/data-drive/engain_dragon_mettatext_A1/`

I would not start coding blindly yet. The next move should be one final, workspace-local A1 implementation plan that names the exact files, contracts, transport, failure behavior, and RED tests. Then we let it implement that plan.

Give the editor this:

> We are now working exclusively inside the preserved A1 integration workspace:
>
> ```text
> /mnt/data-drive/engain_dragon_mettatext_A1/
> ├── dragon/
> ├── engain/
> ├── preservation/
> └── README_A1_WORKSPACE.md
> ```
>
> The originals are canonical references and MUST NOT be modified.
>
> Do not operate on:
>
> ```text
> /mnt/data-drive/godot_engain_3d_avatar
> /home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn
> ```
>
> For this task, work only inside:
>
> ```text
> /mnt/data-drive/engain_dragon_mettatext_A1/dragon
> /mnt/data-drive/engain_dragon_mettatext_A1/engain
> ```
>
> We are beginning:
>
> ```text
> A1 — Dragon ↔ MettaText first real seam
> ```
>
> Frozen architectural objective:
>
> ```text
> Dragon
> → MettaText
> → Vault retrieval
> → bounded source-backed semantic context
> → Dragon reasoning
> ```
>
> This slice does NOT implement authority dispatch.
>
> Explicitly excluded from A1:
>
> ```text
> Cartographer
> Topologist
> GodotSim
> Paradox Machine
> Engionality
> Trixel
> WorldField mutation
> EngAInOS admission
> canon promotion
> deed changes
> editor-execution changes
> 2D Dragon work
> automatic feedback closure
> ```
>
> MettaText may annotate which domain a semantic claim appears relevant to, but it MUST NOT invoke those authorities in A1.
>
> Also preserve the existing deed lane unchanged:
>
> ```text
> Dragon
> → [EDITOR_REQUEST]
> → engain.dragon_request.v1
> → current human authorization gate
> → Hermes Editor
> → receipts / validation / revert
> ```
>
> EngAInOS replacement of that human gate is Phase C, not A1.
>
> ## A1 architectural constraints
>
> Treat:
>
> ```text
> dragon/
> ```
>
> as the canonical Dragon runtime.
>
> The existing 3D runtime will eventually back both the 3D world embodiment and the future 2D UI projection. Do not introduce a second Dragon brain, session, semantic caller, provider pipeline, or deed pipeline.
>
> Treat:
>
> ```text
> engain/tier3/mettaext/
> ```
>
> as the current donor implementation for the intended MettaText semantic-intake system.
>
> The public architectural name is MettaText.
>
> Do not simply make Dragon import `tier3.mettaext` directly.
>
> The boundary must remain:
>
> ```text
> Dragon client
>     ↓
> external MettaText facade
>     ↓
> MettaText internals
>     ↓
> Vault/retrieval implementation
> ```
>
> Dragon must not know:
>
> ```text
> Vault filesystem root
> individual Markdown paths
> Obsidian paths
> database/storage implementation
> Mettaext internal module layout
> ```
>
> ## Known Dragon insertion seam
>
> Previous read-only audit established the provider-bound insertion point as:
>
> ```text
> dragon/hermes_session_adapter.py
>
> HermesSessionAdapter._process_claimed_request()
> ```
>
> after:
>
> ```text
> validated = self._validate_request(payload)
> self._reserve_request(request_id)
> ```
>
> and before:
>
> ```text
> prepare_image_dispatch(...)
> _acquire_dispatch_claim()
> director_bridge.process_player_input(...)
> ```
>
> Re-verify this against the copied source before relying on line numbers.
>
> The reason for this placement is important:
>
> MettaText context must be retrieved and validated before the exact provider-bearing prompt/command is frozen.
>
> Do not perform retrieval inside `_format_messages()`.
>
> `_format_messages()` may only format an already-retrieved and already-validated semantic-context value.
>
> ## Known provider injection seam
>
> Previous audit established:
>
> ```text
> dragon/hermes_session_adapter.py
>
> HermesCLIClient._format_messages(...)
> ```
>
> as the appropriate place to add a distinct provenance channel conceptually equivalent to:
>
> ```text
> <AUTHORED_STORY_CONTEXT>
> ...
> </AUTHORED_STORY_CONTEXT>
> ```
>
> This context MUST remain semantically distinct from:
>
> ```text
> <CONVERSATION_MESSAGE>
> <CURRENT_RUNTIME_PERCEPTION>
> <COORDINATION_REPORT>
> ```
>
> Authored story evidence is NOT:
>
> * player speech,
> * current runtime truth,
> * visual perception,
> * admitted canon merely because MettaText returned it.
>
> ## First task: produce the exact A1 RED → GREEN implementation plan
>
> Do not edit code yet.
>
> Re-read the relevant copied files on both sides and produce a concrete implementation plan.
>
> The plan must specify the exact files to:
>
> ```text
> CREATE
> MODIFY
> LEAVE UNCHANGED
> ```
>
> Do not give generic component names when an exact path can be identified.
>
> ### 1. Define the Dragon → MettaText request contract
>
> Start from the actual existing Dragon request structures.
>
> The smallest anticipated request contains approximately:
>
> ```text
> contract
> request_id
> client_request_id
> query_text
> origin_body
> observation_ref:
>     project_id
>     scene_path
>     capture_id
> trigger_reason
> ```
>
> But verify every field against actual code before freezing it.
>
> Remove anything redundant.
>
> Do not require:
>
> ```text
> shared_session_id
> provider_session_id
> model
> provider
> Vault path
> Markdown path
> authority verdict
> runtime mutation instruction
> requested authority list
> ```
>
> unless actual copied code proves an A1 necessity.
>
> `query_text` should be derived from already validated Dragon/player input.
>
> Dragon should not be required to extract entity/location/domain hints in A1. Semantic classification belongs on the MettaText side.
>
> ### 2. Define the MettaText response contract
>
> The smallest anticipated response needs:
>
> ```text
> contract
> request_id
> client_request_id
> status
> failure_code
> observation_ref
> semantic_claims
> evidence
> confidence / proposal state
> intended domain-routing descriptors
> contradictions
> unresolved material
> warnings
> semantic_context_sha256
> ```
>
> Refine this based on actual donor capabilities.
>
> For every evidence item, determine the strongest provenance that can actually be implemented in this slice.
>
> Preferred evidence identity is based on immutable source content rather than transformed Pass-1 line numbering.
>
> Investigate how to provide at least:
>
> ```text
> opaque logical source identity
> source SHA-256
> exact bounded excerpt
> exact occurrence/span coordinates
> extraction/version identity if necessary
> ```
>
> Do not expose absolute Vault paths to Dragon.
>
> Do not return complete source documents when bounded evidence suffices.
>
> ### 3. Preserve epistemic layers
>
> A1 must not recreate the existing entity-filter collapse.
>
> The response must preserve the distinction between:
>
> ```text
> SOURCE_WITNESS
> SEMANTIC_PROPOSAL
> ```
>
> and later states that A1 does not establish:
>
> ```text
> DOMAIN_FINDING
> GOVERNED/ADMITTED_TRUTH
> ```
>
> Unknown authored entities must remain visible as evidence/proposals even when the current runtime ontology cannot spawn or recognize them.
>
> Do not use runtime renderability as a filter for source witnessing.
>
> ### 4. Design relevant Vault retrieval
>
> Existing `index_vault()` is discovery, not relevance retrieval.
>
> Determine the minimum deterministic retrieval facility necessary for A1.
>
> It must accept a semantic request without Dragon supplying storage paths.
>
> For A1, keep retrieval deliberately small and deterministic.
>
> Define:
>
> ```text
> how candidate documents are selected
> how matches are ranked
> how many results are allowed
> maximum evidence/context bytes
> deterministic tie-breaking
> empty-result behavior
> source-read failure behavior
> duplicate occurrence behavior
> hash calculation
> ```
>
> Do not introduce embeddings, vector databases, remote services, or another AI model unless the existing repository already requires one and you can prove it is necessary for A1.
>
> Prefer a deterministic local proof first.
>
> ### 5. Define the external MettaText facade
>
> Determine the narrowest practical cross-process boundary.
>
> It must live on the EngAIn/MettaText side and hide MettaText internals from Dragon.
>
> Compare reasonable mechanisms using infrastructure that already exists where possible.
>
> We need one request:
>
> ```text
> Dragon worker → MettaText
> ```
>
> and one bounded response:
>
> ```text
> MettaText → Dragon worker
> ```
>
> Do not silently route this through provider dispatch.
>
> The semantic lookup is not a provider turn.
>
> Do not make the Dragon process import donor Python packages across repository boundaries.
>
> Report the selected transport and why it is the smallest compatible seam.
>
> ### 6. Define the provider-neutral Dragon-side client
>
> The client must:
>
> ```text
> construct the bounded request
> call the MettaText facade
> enforce timeout
> enforce response-size limit
> validate exact schema
> validate request correlation
> validate observation correlation
> validate semantic-context hash
> reject malformed/unexpected fields as appropriate
> return one immutable semantic-context value
> ```
>
> It must not:
>
> ```text
> inspect the Vault
> parse chapters itself
> classify story domains itself
> import Mettaext internals
> promote anything to truth
> mutate runtime
> mutate source
> ```
>
> ### 7. Define failure policy explicitly
>
> This cannot remain ambiguous.
>
> For the A1 proof, specify behavior for:
>
> ```text
> MettaText unavailable
> request timeout
> malformed response
> oversized response
> request_id mismatch
> client_request_id mismatch
> capture_id mismatch
> source read failure
> no relevant evidence
> invalid semantic hash
> ```
>
> Distinguish:
>
> ```text
> EMPTY_BUT_VALID
> ```
>
> from:
>
> ```text
> RETRIEVAL_FAILED
> CONTRACT_INVALID
> SERVICE_UNAVAILABLE
> ```
>
> Do not invent story context when retrieval returns nothing.
>
> The proof should fail closed on integrity/contract failures.
>
> Also determine whether an unavailable MettaText service should block the provider turn during A1 proof mode or whether there should be an explicit disabled/bypass configuration.
>
> Do not silently fall through after a failed required lookup.
>
> ### 8. Define temporary A1 trigger policy
>
> We are NOT choosing final production retrieval behavior yet.
>
> The previous audit showed the current Dragon lacks sufficient stable semantic world IDs for an intelligent cache/change-trigger policy and cannot explicitly request MettaText midway through a single provider turn.
>
> Therefore design A1 with an explicit proof configuration such as:
>
> ```text
> forced context retrieval for the designated proof turn
> ```
>
> or another equally bounded mechanism.
>
> Do not accidentally establish “retrieve entire story every Dragon turn forever” as architecture.
>
> Clearly separate:
>
> ```text
> proof trigger
> ```
>
> from:
>
> ```text
> future production trigger policy
> ```
>
> ### 9. Define exact provider injection
>
> The semantic response should appear as its own block, conceptually:
>
> ```text
> <AUTHORED_STORY_CONTEXT>
> PROVENANCE=METTATEXT_SOURCE_WITNESS
> REQUEST_ID=...
> CLIENT_REQUEST_ID=...
> CAPTURE_ID=...
> SEMANTIC_CONTEXT_SHA256=...
> ...
> </AUTHORED_STORY_CONTEXT>
> ```
>
> Determine an encoding that cannot be confused with instructions from the player or with runtime truth.
>
> It should contain bounded structured material rather than raw uncontrolled Vault prose where possible.
>
> Confirm that the exact validated/hash-checked bytes used for semantic context are the exact bytes incorporated into the provider-bearing command.
>
> ### 10. RED tests first
>
> Identify the exact tests to add before implementation.
>
> At minimum, design tests proving:
>
> 1. Dragon request contains no Vault storage implementation details.
> 2. MettaText alone owns source retrieval.
> 3. Request IDs remain correlated.
> 4. Capture/observation correlation remains exact.
> 5. Evidence points to exact source content.
> 6. Source hashes replay correctly.
> 7. Unknown authored entities survive semantic intake.
> 8. Empty retrieval produces explicit empty context.
> 9. Retrieval failure does not fabricate context.
> 10. Malformed response fails closed.
> 11. Oversized response fails closed.
> 12. Hash mismatch fails closed.
> 13. Authored context is injected separately from player text.
> 14. Authored context is injected separately from runtime perception.
> 15. Existing `[EDITOR_REQUEST]` behavior remains unchanged.
> 16. Existing provider response remains OBSERVATION-only.
> 17. No authority is invoked.
> 18. Neither Vault nor runtime state is mutated.
>
> Also identify regression tests required on both copied repositories.
>
> ### 11. GREEN proof
>
> Define one deterministic end-to-end fixture.
>
> It should prove:
>
> ```text
> known authored source in Vault
>     ↓
> real Dragon request
>     ↓
> external MettaText call
>     ↓
> bounded retrieval
>     ↓
> semantic extraction
>     ↓
> source-backed response
>     ↓
> Dragon validation
>     ↓
> separate AUTHORED_STORY_CONTEXT injection
>     ↓
> exact existing provider invocation path
> ```
>
> The provider does not need to mutate anything.
>
> The test must demonstrate that the provider receives the semantic context through the real Dragon path, not through a mocked replacement of the whole Dragon pipeline.
>
> ### 12. Preserve current behavior
>
> A1 must not change:
>
> ```text
> runtime perception capture
> PNG hashing
> provider session continuity
> replay prevention
> presence/session claim behavior
> Dragon response mailbox
> [EDITOR_REQUEST] parsing
> human Execute gate
> Hermes Editor DIRECT_WRITE behavior
> edit receipts
> revert
> project validation
> ```
>
> If implementation would require changing one of these, stop and explain why before coding.
>
> ## Deliverable
>
> Return:
>
> ```text
> A1 RED → GREEN IMPLEMENTATION PLAN
>
> 1. Current call chain
> 2. Files to create
> 3. Files to modify
> 4. Files explicitly unchanged
> 5. Request schema
> 6. Response schema
> 7. MettaText facade design
> 8. Retrieval design
> 9. Dragon client design
> 10. Failure policy
> 11. Provider injection design
> 12. RED tests
> 13. GREEN proof
> 14. Regression test set
> 15. Exact implementation order
> 16. Risks / unresolved decisions
> ```
>
> Every proposed code change must identify the exact function/class it affects.
>
> Do not implement yet.
>
> Do not commit.
>
> Do not push.
>
> Stop after the plan for review.

Once he returns that plan, we can inspect it for scope creep or wrong assumptions. If it is clean, that becomes the specification for the first actual implementation in the copied workspace.

The preservation work was worth doing. We can now be aggressive inside A1 without gambling the working Dragon.
